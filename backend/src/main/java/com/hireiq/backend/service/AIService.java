package com.hireiq.backend.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.*;
import java.util.Map;
import java.util.HashMap;

@Service
public class AIService {

    // Python FastAPI URL — from application.properties
    @Value("${ai.service.url:http://localhost:8000}")
    private String aiServiceUrl;

    private final RestTemplate restTemplate;

    public AIService() {
        this.restTemplate = new RestTemplate();
    }

    /**
     * Call Python AI service with any endpoint and request body.
     * Reusable method — like a generic HTTP client.
     */
    private Map callAIService(String endpoint, Map<String, Object> body) {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        HttpEntity<Map<String, Object>> request =
            new HttpEntity<>(body, headers);

        ResponseEntity<Map> response = restTemplate.postForEntity(
            aiServiceUrl + endpoint,
            request,
            Map.class
        );

        return response.getBody();
    }

    // ── CHAT ─────────────────────────────────────────────────
    public Map chat(String message) {
        Map<String, Object> body = new HashMap<>();
        body.put("message", message);
        return callAIService("/api/chat", body);
    }

    // ── JD ANALYZER ──────────────────────────────────────────
    public Map analyzeJD(String jobDescription) {
        Map<String, Object> body = new HashMap<>();
        body.put("job_description", jobDescription);
        return callAIService("/api/analyze-jd", body);
    }

    // ── RESUME ANALYZER ──────────────────────────────────────
    public Map analyzeResume(String resume, String jobDescription) {
        Map<String, Object> body = new HashMap<>();
        body.put("resume", resume);
        body.put("job_description", jobDescription);
        return callAIService("/api/analyze-resume", body);
    }

    // ── COVER LETTER ─────────────────────────────────────────
    public Map generateCoverLetter(
            String resume,
            String jobDescription,
            String companyName,
            String tone) {

        Map<String, Object> body = new HashMap<>();
        body.put("resume", resume);
        body.put("job_description", jobDescription);
        body.put("company_name", companyName);
        body.put("tone", tone);
        return callAIService("/api/cover-letter", body);
    }
}