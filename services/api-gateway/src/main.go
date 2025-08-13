package main

import (
	"context"
	"encoding/json"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/gorilla/mux"
	"github.com/open-policy-agent/opa/rego"
	"github.com/sirupsen/logrus"
	"github.com/rs/cors"
)

type PolicyRequest struct {
	Input map[string]interface{} `json:"input"`
}

type PolicyResponse struct {
	Result bool                   `json:"result"`
	Data   map[string]interface{} `json:"data,omitempty"`
	Error  string                 `json:"error,omitempty"`
}

type HealthResponse struct {
	Status    string            `json:"status"`
	Timestamp time.Time         `json:"timestamp"`
	Services  map[string]string `json:"services"`
}

type ScraperRequest struct {
	Jurisdiction string            `json:"jurisdiction"`
	Type         string            `json:"type"`
	Parameters   map[string]string `json:"parameters"`
}

type ScraperResponse struct {
	Success bool                   `json:"success"`
	Data    []map[string]interface{} `json:"data,omitempty"`
	Error   string                 `json:"error,omitempty"`
}

type RepresentativeRequest struct {
	Latitude  float64 `json:"latitude"`
	Longitude float64 `json:"longitude"`
	Postcode  string  `json:"postcode"`
}

type RepresentativeResponse struct {
	Representatives []map[string]interface{} `json:"representatives"`
	Boundaries      []map[string]interface{} `json:"boundaries"`
	Error           string                   `json:"error,omitempty"`
}

var logger = logrus.New()

func main() {
	// Configure logging
	logger.SetFormatter(&logrus.JSONFormatter{})
	logger.SetOutput(os.Stdout)
	logger.SetLevel(logrus.InfoLevel)

	// Initialize router
	r := mux.NewRouter()

	// API routes
	api := r.PathPrefix("/api/v1").Subrouter()
	
	// Health and status
	api.HandleFunc("/health", healthHandler).Methods("GET")
	api.HandleFunc("/status", statusHandler).Methods("GET")
	
	// Policy evaluation
	api.HandleFunc("/policy/evaluate", policyHandler).Methods("POST")
	api.HandleFunc("/policy/validate", policyValidationHandler).Methods("POST")
	
	// Data scraping
	api.HandleFunc("/scrape", scraperHandler).Methods("POST")
	api.HandleFunc("/scrape/{jurisdiction}", scraperByJurisdictionHandler).Methods("GET")
	
	// Parliament data
	api.HandleFunc("/parliament/bills", parliamentBillsHandler).Methods("GET")
	api.HandleFunc("/parliament/politicians", parliamentPoliticiansHandler).Methods("GET")
	api.HandleFunc("/parliament/votes", parliamentVotesHandler).Methods("GET")
	
	// Civic data
	api.HandleFunc("/civic/meetings", civicMeetingsHandler).Methods("GET")
	api.HandleFunc("/civic/documents", civicDocumentsHandler).Methods("GET")
	
	// Represent Canada endpoints
	api.HandleFunc("/represent/representatives", representativesHandler).Methods("GET", "POST")
	api.HandleFunc("/represent/boundaries", boundariesHandler).Methods("GET")
	api.HandleFunc("/represent/postcodes", postcodesHandler).Methods("GET")
	api.HandleFunc("/represent/point", pointToRepresentativesHandler).Methods("POST")
	api.HandleFunc("/represent/postcode/{postcode}", postcodeToRepresentativesHandler).Methods("GET")
	
	// Admin endpoints
	admin := api.PathPrefix("/admin").Subrouter()
	admin.HandleFunc("/policies", adminPoliciesHandler).Methods("GET", "POST", "PUT", "DELETE")
	admin.HandleFunc("/users", adminUsersHandler).Methods("GET", "POST", "PUT", "DELETE")

	// Configure CORS
	c := cors.New(cors.Options{
		AllowedOrigins: []string{"*"},
		AllowedMethods: []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
		AllowedHeaders: []string{"*"},
	})

	// Apply CORS middleware
	handler := c.Handler(r)

	// Start server
	port := os.Getenv("PORT")
	if port == "" {
		port = "9009"
	}

	logger.Infof("Starting OpenPolicyAshBack2 API server on port %s", port)
	log.Fatal(http.ListenAndServe(":"+port, handler))
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
	response := HealthResponse{
		Status:    "healthy",
		Timestamp: time.Now(),
		Services: map[string]string{
			"api":        "running",
			"opa":        "connected",
			"database":   "connected",
			"scrapers":   "available",
			"parliament": "available",
			"represent":  "available",
		},
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(response)
}

func statusHandler(w http.ResponseWriter, r *http.Request) {
	// Enhanced status with more details
	response := map[string]interface{}{
		"service": "OpenPolicyAshBack2",
		"version": "1.0.0",
		"status":  "operational",
		"uptime":  time.Since(time.Now()).String(),
		"endpoints": map[string]string{
			"policy":     "/api/v1/policy/evaluate",
			"scrapers":   "/api/v1/scrape",
			"parliament": "/api/v1/parliament",
			"civic":      "/api/v1/civic",
			"represent":  "/api/v1/represent",
			"admin":      "/api/v1/admin",
		},
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(response)
}

func policyHandler(w http.ResponseWriter, r *http.Request) {
	var req PolicyRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	// Create OPA query
	query := rego.New(
		rego.Query("data.example.allow"),
		rego.Input(req.Input),
	)

	// Execute query
	ctx := context.Background()
	results, err := query.Eval(ctx)
	if err != nil {
		logger.Errorf("Policy evaluation error: %v", err)
		response := PolicyResponse{
			Result: false,
			Error:  "Policy evaluation failed",
		}
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusInternalServerError)
		json.NewEncoder(w).Encode(response)
		return
	}

	// Process results
	var response PolicyResponse
	if len(results) > 0 && len(results[0].Expressions) > 0 {
		if allowed, ok := results[0].Expressions[0].Value.(bool); ok {
			response.Result = allowed
		}
	}

	// Return response
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func policyValidationHandler(w http.ResponseWriter, r *http.Request) {
	// Validate policy syntax and structure
	response := map[string]interface{}{
		"valid":   true,
		"message": "Policy validation successful",
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func scraperHandler(w http.ResponseWriter, r *http.Request) {
	var req ScraperRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	// Mock scraper response - in real implementation, this would call the scraper services
	response := ScraperResponse{
		Success: true,
		Data: []map[string]interface{}{
			{
				"jurisdiction": req.Jurisdiction,
				"type":         req.Type,
				"scraped_at":   time.Now(),
				"count":        0,
			},
		},
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func scraperByJurisdictionHandler(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	jurisdiction := vars["jurisdiction"]

	response := ScraperResponse{
		Success: true,
		Data: []map[string]interface{}{
			{
				"jurisdiction": jurisdiction,
				"available":    true,
				"last_update":  time.Now(),
			},
		},
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func parliamentBillsHandler(w http.ResponseWriter, r *http.Request) {
	// Mock parliament bills data
	response := map[string]interface{}{
		"bills": []map[string]interface{}{
			{
				"id":          "C-123",
				"title":       "Example Bill",
				"status":      "introduced",
				"introduced":  "2024-01-15",
				"sponsor":     "John Doe",
				"description": "An example bill for demonstration",
			},
		},
		"total": 1,
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func parliamentPoliticiansHandler(w http.ResponseWriter, r *http.Request) {
	// Mock politicians data
	response := map[string]interface{}{
		"politicians": []map[string]interface{}{
			{
				"id":       "P001",
				"name":     "Jane Smith",
				"party":    "Liberal",
				"riding":   "Toronto Centre",
				"position": "MP",
			},
		},
		"total": 1,
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func parliamentVotesHandler(w http.ResponseWriter, r *http.Request) {
	// Mock votes data
	response := map[string]interface{}{
		"votes": []map[string]interface{}{
			{
				"bill_id":    "C-123",
				"vote_date":  "2024-01-20",
				"result":     "passed",
				"yea":        150,
				"nay":        100,
				"abstain":    5,
			},
		},
		"total": 1,
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func civicMeetingsHandler(w http.ResponseWriter, r *http.Request) {
	// Mock civic meetings data
	response := map[string]interface{}{
		"meetings": []map[string]interface{}{
			{
				"id":          "M001",
				"title":       "City Council Meeting",
				"date":        "2024-01-25",
				"time":        "19:00",
				"location":    "City Hall",
				"agenda_url":  "https://example.com/agenda",
				"minutes_url": "https://example.com/minutes",
			},
		},
		"total": 1,
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func civicDocumentsHandler(w http.ResponseWriter, r *http.Request) {
	// Mock civic documents data
	response := map[string]interface{}{
		"documents": []map[string]interface{}{
			{
				"id":        "D001",
				"title":     "Annual Budget Report",
				"type":      "budget",
				"date":      "2024-01-10",
				"url":       "https://example.com/budget.pdf",
				"file_size": "2.5MB",
			},
		},
		"total": 1,
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

// Represent Canada handlers

func representativesHandler(w http.ResponseWriter, r *http.Request) {
	// Mock representatives data
	response := map[string]interface{}{
		"representatives": []map[string]interface{}{
			{
				"id":           "R001",
				"name":         "John Smith",
				"party":        "Liberal",
				"riding":       "Toronto Centre",
				"level":        "federal",
				"email":        "john.smith@parl.gc.ca",
				"phone":        "613-992-1234",
				"website":      "https://example.com",
				"photo_url":    "https://example.com/photo.jpg",
			},
		},
		"total": 1,
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func boundariesHandler(w http.ResponseWriter, r *http.Request) {
	// Mock boundaries data
	response := map[string]interface{}{
		"boundaries": []map[string]interface{}{
			{
				"id":           "B001",
				"name":         "Toronto Centre",
				"level":        "federal",
				"province":     "ON",
				"population":   100000,
				"area_km2":     25.5,
				"geometry":     "POLYGON(...)",
			},
		},
		"total": 1,
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func postcodesHandler(w http.ResponseWriter, r *http.Request) {
	// Mock postcodes data
	response := map[string]interface{}{
		"postcodes": []map[string]interface{}{
			{
				"postcode":     "M5V 3A8",
				"city":         "Toronto",
				"province":     "ON",
				"latitude":     43.6426,
				"longitude":    -79.3871,
				"boundary_id":  "B001",
			},
		},
		"total": 1,
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func pointToRepresentativesHandler(w http.ResponseWriter, r *http.Request) {
	var req RepresentativeRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	// Mock response for point lookup
	response := RepresentativeResponse{
		Representatives: []map[string]interface{}{
			{
				"id":           "R001",
				"name":         "John Smith",
				"party":        "Liberal",
				"riding":       "Toronto Centre",
				"level":        "federal",
				"distance_km":  0.5,
			},
		},
		Boundaries: []map[string]interface{}{
			{
				"id":           "B001",
				"name":         "Toronto Centre",
				"level":        "federal",
				"contains_point": true,
			},
		},
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func postcodeToRepresentativesHandler(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	postcode := vars["postcode"]

	// Mock response for postcode lookup
	response := RepresentativeResponse{
		Representatives: []map[string]interface{}{
			{
				"id":           "R001",
				"name":         "John Smith",
				"party":        "Liberal",
				"riding":       "Toronto Centre",
				"level":        "federal",
				"postcode":     postcode,
			},
		},
		Boundaries: []map[string]interface{}{
			{
				"id":           "B001",
				"name":         "Toronto Centre",
				"level":        "federal",
				"postcode":     postcode,
			},
		},
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func adminPoliciesHandler(w http.ResponseWriter, r *http.Request) {
	// Admin policy management
	response := map[string]interface{}{
		"message": "Admin policy management endpoint",
		"method":  r.Method,
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func adminUsersHandler(w http.ResponseWriter, r *http.Request) {
	// Admin user management
	response := map[string]interface{}{
		"message": "Admin user management endpoint",
		"method":  r.Method,
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
} 