# coding: utf-8
"""
Core models for OpenPolicyMerge Django backend.
This contains the fundamental political entities that the entire system depends on.
"""

import datetime
from django.db import models
from django.urls import reverse
from django.template.defaultfilters import slugify
from django.conf import settings

from .utils import memoize_property, ActiveManager, language_property
from .parsetools import normalizeName

import logging
logger = logging.getLogger(__name__)

class PartyManager(models.Manager):
    """Manager for Party objects with custom query methods."""
    
    def get_by_name(self, name):
        """Get a party by name, handling variations."""
        name = name.strip().lower()
        try:
            return PartyAlternateName.objects.get(name=name).party
        except PartyAlternateName.DoesNotExist:
            raise Party.DoesNotExist()

class Party(models.Model):
    """A federal political party."""
    name_en = models.CharField(max_length=100)
    name_fr = models.CharField(max_length=100, blank=True)
    short_name_en = models.CharField(max_length=100, blank=True)
    short_name_fr = models.CharField(max_length=100, blank=True)
    slug = models.CharField(max_length=10, blank=True)
    
    name = language_property('name')
    short_name = language_property('short_name')
    
    objects = PartyManager()
    
    class Meta:
        verbose_name_plural = 'Parties'

    def save(self, *args, **kwargs):
        if not self.name_fr:
            self.name_fr = self.name_en
        if not self.short_name_en:
            self.short_name_en = self.name_en
        if not self.short_name_fr:
            self.short_name_fr = self.name_fr
        super(Party, self).save(*args, **kwargs)
        self.add_alternate_name(self.name_en)
        self.add_alternate_name(self.name_fr)

    def add_alternate_name(self, name):
        """Add an alternate name for this party."""
        name = name.strip().lower()
        PartyAlternateName.objects.get_or_create(name=name, party=self)
                
    def __str__(self):
        return self.name_en

class PartyAlternateName(models.Model):
    """Alternate names for parties to handle variations."""
    name = models.CharField(max_length=100, primary_key=True)
    party = models.ForeignKey(Party, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.name} -> {self.party.name_en}"

class Person(models.Model):
    """Abstract base class for models representing a person."""
    name = models.CharField(max_length=100)
    name_given = models.CharField("Given name", max_length=50, blank=True)
    name_family = models.CharField("Family name", max_length=50, blank=True)

    def __str__(self):
        return self.name
    
    class Meta:
        abstract = True
        ordering = ('name',)

class PoliticianManager(models.Manager):
    """Manager for Politician objects with custom query methods."""
    
    def elected(self):
        """Returns a QuerySet of all politicians that were once elected to office."""
        return self.get_queryset().annotate(
            electedcount=models.Count('electedmember')).filter(electedcount__gte=1)
            
    def never_elected(self):
        """Returns a QuerySet of all politicians that were never elected as MPs."""
        return self.get_queryset().filter(electedmember__isnull=True)
        
    def current(self):
        """Returns a QuerySet of all current MPs."""
        return self.get_queryset().filter(electedmember__end_date__isnull=True,
            electedmember__start_date__isnull=False).distinct()
        
    def elected_but_not_current(self):
        """Returns a QuerySet of former MPs."""
        return self.get_queryset().exclude(electedmember__end_date__isnull=True)
    
    def filter_by_name(self, name):
        """Returns a list of politicians matching a given name."""
        return [i.politician for i in 
            PoliticianInfo.objects.filter(schema='alternate_name', value=normalizeName(name))]
    
    def get_by_name(self, name, session=None, riding=None, election=None, party=None, saveAlternate=True, strictMatch=False):
        """Return a Politician by name with various matching strategies."""
        poss = PoliticianInfo.objects.filter(schema='alternate_name', value=normalizeName(name))
        if len(poss) >= 1:
            if session or riding or party:
                result = None
                for p in poss:
                    members = ElectedMember.objects.filter(politician=p.politician)
                    if riding: members = members.filter(riding=riding)
                    if session: members = members.filter(sessions=session)
                    if party: members = members.filter(party=party)
                    if len(members) >= 1:
                        if result:
                            raise Politician.MultipleObjectsReturned(name)
                        result = members[0].politician
                if result:
                    return result
            elif len(poss) > 1:
                raise Politician.MultipleObjectsReturned(name)
            else:
                return poss[0].politician
        
        if session and not strictMatch:
            # Try matching on last name only
            import re
            match = re.search(r'\s([A-Z][\w-]+)$', name.strip())
            if match:
                lastname = match.group(1)
                pols = self.get_queryset().filter(name_family=lastname, electedmember__sessions=session).distinct()
                if riding:
                    pols = pols.filter(electedmember__riding=riding)
                if len(pols) > 1:
                    if riding:
                        raise Exception("DATA ERROR: Multiple politicians with same last name in same riding/session")
                elif len(pols) == 1:
                    pol = pols[0]
                    if saveAlternate:
                        pol.add_alternate_name(name)
                    return pol
        
        raise Politician.DoesNotExist("Could not find politician named %s" % name)

    def get_by_slug_or_id(self, slug_or_id):
        """Get politician by slug or ID."""
        if slug_or_id.isdigit():
            return self.get(id=slug_or_id)
        return self.get(slug=slug_or_id)

class Politician(Person):
    """Someone who has run for federal office."""
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )

    gender = models.CharField(max_length=1, blank=True, choices=GENDER_CHOICES)
    headshot = models.ImageField(upload_to='polpics', blank=True, null=True)
    headshot_thumbnail = models.ImageField(blank=True, null=True, upload_to='polpics/thumbnail')
    slug = models.CharField(max_length=30, blank=True, db_index=True)
    
    objects = PoliticianManager()
    
    def add_alternate_name(self, name):
        """Add an alternate name for this politician."""
        normname = normalizeName(name)
        if normname not in self.alternate_names():
            self.set_info_multivalued('alternate_name', normname)

    def alternate_names(self):
        """Returns a list of ways of writing this politician's name."""
        return self.politicianinfo_set.filter(schema='alternate_name').values_list('value', flat=True)
        
    def add_slug(self):
        """Assigns a slug to this politician, unless there's a conflict."""
        if self.slug:
            return True
        slug = slugify(self.name)
        if Politician.objects.filter(slug=slug).exists():
            logger.warning("Slug %s already taken" % slug)
            return False
        self.slug = slug
        self.save()
        
    @property
    @memoize_property
    def current_member(self):
        """If this politician is a current MP, returns the corresponding ElectedMember object."""
        try:
            return ElectedMember.objects.get(politician=self, end_date__isnull=True)
        except ElectedMember.DoesNotExist:
            return False

    @property
    @memoize_property        
    def latest_member(self):
        """Returns the most recent ElectedMember object for this politician."""
        try:
            return self.electedmember_set.order_by('-start_date').select_related('party', 'riding')[0]
        except IndexError:
            return None
        
    def save(self, *args, **kwargs):
        super(Politician, self).save(*args, **kwargs)
        self.add_alternate_name(self.name)
            
    def get_absolute_url(self):
        if self.slug:
            return reverse('politician', kwargs={'pol_slug': self.slug})
        return reverse('politician', kwargs={'pol_id': self.id})

    @property
    def identifier(self):
        return self.slug if self.slug else self.id

    @property
    def parlpage(self):
        """Get the Parliament of Canada page URL for this politician."""
        parlid = self.info().get('parl_mp_id')
        if parlid:
            return f"https://www.ourcommons.ca/members/{settings.LANGUAGE_CODE}/{self.identifier}({parlid})"
        return None
        
    def get_contact_url(self):
        if self.slug:
            return reverse('politician_contact', kwargs={'pol_slug': self.slug})
        return reverse('politician_contact', kwargs={'pol_id': self.id})
            
    @memoize_property
    def info(self):
        """Returns a dictionary of PoliticianInfo attributes for this politician."""
        return dict([i for i in self.politicianinfo_set.all().values_list('schema', 'value')])
        
    @memoize_property
    def info_multivalued(self):
        """Returns a dictionary of PoliticianInfo attributes where each key is a list."""
        info = {}
        for i in self.politicianinfo_set.all().values_list('schema', 'value'):
            info.setdefault(i[0], []).append(i[1])
        return info
        
    def set_info(self, key, value, overwrite=True):
        """Set a key-value attribute for this politician."""
        try:
            info = self.politicianinfo_set.get(schema=key)
            if not overwrite:
                raise ValueError("Cannot overwrite key %s on %s with %s" % (key, self, value))
        except PoliticianInfo.DoesNotExist:
            info = PoliticianInfo(politician=self, schema=key)
        except PoliticianInfo.MultipleObjectsReturned:
            logger.error("Multiple objects found for schema %s on politician %r" % (key, self))
            self.politicianinfo_set.filter(schema=key).delete()
            info = PoliticianInfo(politician=self, schema=key)
        info.value = str(value)
        info.save()
        
    def set_info_multivalued(self, key, value):
        """Set a multi-valued attribute for this politician."""
        PoliticianInfo.objects.get_or_create(politician=self, schema=key, value=str(value))

    def del_info(self, key):
        """Delete an attribute for this politician."""
        self.politicianinfo_set.filter(schema=key).delete()

class PoliticianInfoManager(models.Manager):
    """Custom manager ensures we always pull in the politician FK."""
    
    def get_queryset(self):
        return super(PoliticianInfoManager, self).get_queryset().select_related('politician')

class PoliticianInfo(models.Model):
    """Key-value store for attributes of a Politician."""
    politician = models.ForeignKey(Politician, on_delete=models.CASCADE)
    schema = models.CharField(max_length=40, db_index=True)
    value = models.TextField()
    created = models.DateTimeField(blank=True, null=True, default=datetime.datetime.now)
    
    objects = models.Manager()
    sr_objects = PoliticianInfoManager()
    
    def __str__(self):
        return "%s: %s" % (self.politician, self.schema)
        
    @property
    def int_value(self):
        return int(self.value)

class SessionManager(models.Manager):
    """Manager for Session objects with custom query methods."""
    
    def with_bills(self):
        return self.get_queryset().filter(bill__number_only__gt=1).distinct()
    
    def current(self):
        return self.get_queryset().order_by('-start')[0]

    def get_by_date(self, date):
        return self.filter(models.Q(end__isnull=True) | models.Q(end__gte=date)).get(start__lte=date)

    def get_from_string(self, string):
        """Given a string like '41st Parliament, 1st Session, returns the session."""
        import re
        match = re.search(r'^(\d\d)\D+(\d)\D', string)
        if not match:
            raise ValueError("Could not find parl/session in %s" % string)
        pk = match.group(1) + '-' + match.group(2)
        return self.get_queryset().get(pk=pk)

class Session(models.Model):
    """A session of Parliament."""
    id = models.CharField(max_length=4, primary_key=True)
    name = models.CharField(max_length=100)
    start = models.DateField()
    end = models.DateField(blank=True, null=True)
    parliamentnum = models.IntegerField(blank=True, null=True)
    sessnum = models.IntegerField(blank=True, null=True)

    objects = SessionManager()
    
    class Meta:
        ordering = ('-start',)

    def __str__(self):
        return self.name
        
    def has_votes(self):
        return bool(self.votequestion_set.all().count())

class RidingManager(models.Manager):
    """Manager for Riding objects with custom query methods."""
    
    def get_by_name(self, name, current=True):
        """Get a riding by name, handling variations."""
        slug = slugify(name)
        qs = self.get_queryset()
        if current:
            qs = qs.filter(current=True)
        return qs.get(slug=slug)

class Riding(models.Model):
    """A federal riding (electoral district)."""
    name_en = models.CharField(max_length=200)
    name_fr = models.CharField(blank=True, max_length=200)
    province = models.CharField(max_length=2)
    slug = models.CharField(max_length=60, unique=True, db_index=True)
    edid = models.IntegerField(blank=True, null=True, db_index=True)
    current = models.BooleanField(blank=True, default=False)
    
    objects = RidingManager()
    
    name = language_property('name')
    
    class Meta:
        ordering = ('province', 'name_en')
        
    def save(self):
        if not self.slug:
            self.slug = slugify(self.name_en)
        super(Riding, self).save()
        
    def __str__(self):
        return "%s (%s)" % (self.name_en, self.province)

class ElectedMemberManager(models.Manager):
    """Manager for ElectedMember objects with custom query methods."""
    
    def current(self):
        return self.get_queryset().filter(end_date__isnull=True)
        
    def former(self):
        return self.get_queryset().filter(end_date__isnull=False)
    
    def on_date(self, date):
        return self.get_queryset().filter(
            models.Q(start_date__lte=date) & 
            (models.Q(end_date__isnull=True) | models.Q(end_date__gte=date))
        )
    
    def get_by_pol(self, politician, date=None, session=None):
        """Get elected member for a politician on a specific date or session."""
        if not date and not session:
            raise Exception("Provide either a date or a session to get_by_pol.")
        if date:
            return self.on_date(date).get(politician=politician)
        else:
            qs = self.get_queryset().filter(politician=politician, sessions=session).order_by('-start_date')
            if not len(qs):
                raise ElectedMember.DoesNotExist("No elected member for %s, session %s" % (politician, session))
            return qs[0]

class ElectedMember(models.Model):
    """Represents one person, elected to a given riding for a given party."""
    sessions = models.ManyToManyField(Session)
    politician = models.ForeignKey(Politician, on_delete=models.CASCADE)
    riding = models.ForeignKey(Riding, on_delete=models.CASCADE)
    party = models.ForeignKey(Party, on_delete=models.CASCADE)
    start_date = models.DateField(db_index=True)
    end_date = models.DateField(blank=True, null=True, db_index=True)
    
    objects = ElectedMemberManager()
    
    class Meta:
        ordering = ('-start_date',)

    def __str__(self):
        if self.end_date:
            return "%s (%s) was the member from %s from %s to %s" % (
                self.politician, self.party, self.riding, self.start_date, self.end_date)
        else:
            return "%s (%s) is the member from %s (since %s)" % (
                self.politician, self.party, self.riding, self.start_date)

    def to_api_dict(self, representation, include_politician=True):
        """Convert to API dictionary format."""
        d = dict(
            url=self.get_absolute_url(),
            start_date=str(self.start_date),
            end_date=str(self.end_date) if self.end_date else None,
            party={
                'name': {'en': self.party.name_en},
                'short_name': {'en': self.party.short_name_en}
            },
            label={'en': "%s MP for %s" % (self.party.short_name_en, self.riding.name_en)},
            riding={
                'name': {'en': self.riding.name_en},
                'province': self.riding.province,
                'id': self.riding.edid,
            }
        )
        if include_politician:
            d['politician_url'] = self.politician.get_absolute_url()
        return d

    def get_absolute_url(self):
        return reverse('politician_membership', kwargs={'member_id': self.id})
            
    @property
    def current(self):
        return not bool(self.end_date)

class RidingPostcodeCache(models.Model):
    """Cache of which riding a postcode is in."""
    postcode = models.CharField(max_length=6, primary_key=True)
    riding = models.ForeignKey(Riding, on_delete=models.CASCADE)
    source = models.CharField(max_length=30, blank=True)
    timestamp = models.DateTimeField(default=datetime.datetime.now)
    
    def __str__(self):
        return f"{self.postcode} -> {self.riding.name_en}"

class SiteNews(models.Model):
    """Entries for the semi-blog on the openparliament homepage."""
    date = models.DateTimeField(default=datetime.datetime.now)
    title = models.CharField(max_length=200)
    text = models.TextField()
    active = models.BooleanField(default=True)
    
    objects = models.Manager()
    public = ActiveManager()
    
    def html(self):
        """Convert markdown text to HTML."""
        try:
            from markdown import markdown
            from django.utils.safestring import mark_safe
            return mark_safe(markdown(self.text))
        except ImportError:
            return self.text
    
    class Meta:
        ordering = ('-date',)

