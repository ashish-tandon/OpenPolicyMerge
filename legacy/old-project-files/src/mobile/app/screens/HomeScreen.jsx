import React from 'react';
import { View, Text, ScrollView, TouchableOpacity, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

export default function HomeScreen() {
  const features = [
    {
      id: 1,
      title: 'Policy Management',
      description: 'Evaluate and manage policies using Open Policy Agent',
      icon: 'shield',
      color: '#3b82f6'
    },
    {
      id: 2,
      title: 'Representatives',
      description: 'Find Canadian elected officials and electoral boundaries',
      icon: 'people',
      color: '#10b981'
    },
    {
      id: 3,
      title: 'Parliamentary Data',
      description: 'Access comprehensive Canadian legislative data',
      icon: 'business',
      color: '#8b5cf6'
    },
    {
      id: 4,
      title: 'Civic Information',
      description: 'Municipal government data and documents',
      icon: 'city',
      color: '#f59e0b'
    }
  ];

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Welcome to OpenPolicy Merge</Text>
        <Text style={styles.subtitle}>
          A unified civic data platform for Canadian legislative and policy data
        </Text>
      </View>

      <View style={styles.featuresContainer}>
        {features.map((feature) => (
          <TouchableOpacity key={feature.id} style={styles.featureCard}>
            <View style={[styles.iconContainer, { backgroundColor: feature.color }]}>
              <Ionicons name={feature.icon} size={24} color="white" />
            </View>
            <View style={styles.featureContent}>
              <Text style={styles.featureTitle}>{feature.title}</Text>
              <Text style={styles.featureDescription}>{feature.description}</Text>
            </View>
          </TouchableOpacity>
        ))}
      </View>

      <View style={styles.statsContainer}>
        <Text style={styles.statsTitle}>Platform Statistics</Text>
        <View style={styles.statsGrid}>
          <View style={styles.statItem}>
            <Text style={styles.statNumber}>9</Text>
            <Text style={styles.statLabel}>Repositories</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={styles.statNumber}>6.5GB</Text>
            <Text style={styles.statLabel}>Data</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={styles.statNumber}>15+</Text>
            <Text style={styles.statLabel}>APIs</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={styles.statNumber}>12</Text>
            <Text style={styles.statLabel}>Services</Text>
          </View>
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f9fafb',
  },
  header: {
    padding: 20,
    alignItems: 'center',
    backgroundColor: 'white',
    marginBottom: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1f2937',
    textAlign: 'center',
    marginBottom: 10,
  },
  subtitle: {
    fontSize: 16,
    color: '#6b7280',
    textAlign: 'center',
    lineHeight: 22,
  },
  featuresContainer: {
    paddingHorizontal: 20,
    marginBottom: 20,
  },
  featureCard: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    flexDirection: 'row',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  iconContainer: {
    width: 48,
    height: 48,
    borderRadius: 24,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  featureContent: {
    flex: 1,
  },
  featureTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1f2937',
    marginBottom: 4,
  },
  featureDescription: {
    fontSize: 14,
    color: '#6b7280',
    lineHeight: 20,
  },
  statsContainer: {
    backgroundColor: 'white',
    marginHorizontal: 20,
    marginBottom: 20,
    borderRadius: 12,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  statsTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#1f2937',
    textAlign: 'center',
    marginBottom: 20,
  },
  statsGrid: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  statItem: {
    alignItems: 'center',
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#3b82f6',
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    color: '#6b7280',
    textAlign: 'center',
  },
});
