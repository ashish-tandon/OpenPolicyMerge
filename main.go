package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"

	"github.com/gorilla/mux"
	"github.com/open-policy-agent/opa/rego"
	"github.com/sirupsen/logrus"
)

type PolicyRequest struct {
	Input map[string]interface{} `json:"input"`
}

type PolicyResponse struct {
	Result bool                   `json:"result"`
	Data   map[string]interface{} `json:"data,omitempty"`
}

var logger = logrus.New()

func main() {
	// Configure logging
	logger.SetFormatter(&logrus.JSONFormatter{})
	logger.SetOutput(os.Stdout)
	logger.SetLevel(logrus.InfoLevel)

	// Initialize router
	r := mux.NewRouter()

	// Define routes
	r.HandleFunc("/health", healthHandler).Methods("GET")
	r.HandleFunc("/policy/evaluate", policyHandler).Methods("POST")

	// Start server
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	logger.Infof("Starting server on port %s", port)
	log.Fatal(http.ListenAndServe(":"+port, r))
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(map[string]string{"status": "healthy"})
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
		http.Error(w, "Policy evaluation failed", http.StatusInternalServerError)
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