package com.hireiq.backend.controller;

import com.hireiq.backend.service.AIService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.Map;
import java.util.HashMap;

@RestController
@RequestMapping("/api")
@CrossOrigin(origins = "*") // Allow frontend to call this API
public class HireIQController {

    @Autowired
    private AIService aiService;

    // ── HEALTH CHECK ─────────────────────────────────────────
    @GetMapping("/health")
    public ResponseEntity<Map> health() {
        Map<String, String> response = new HashMap<>();
        response.put("status", "Spring Boot HireIQ is running! ☕");
        response.put("version", "1.0.0");
        return ResponseEntity.ok(response);
    }

    // ── CHAT ─────────────────────────────────────────────────
    @PostMapping("/chat")
    public ResponseEntity<Map> chat(@RequestBody Map<String, String> request) {
        String message = request.get("message");
        Map result = aiService.chat(message);
        return ResponseEntity.ok(result);
    }

    // ── JD ANALYZER ──────────────────────────────────────────
    @PostMapping("/analyze-jd")
    public ResponseEntity<Map> analyzeJD(@RequestBody Map<String, String> request) {
        String jd = request.get("job_description");
        Map result = aiService.analyzeJD(jd);
        return ResponseEntity.ok(result);
    }

    // ── RESUME ANALYZER ──────────────────────────────────────
    @PostMapping("/analyze-resume")
    public ResponseEntity<Map> analyzeResume(@RequestBody Map<String, String> request) {
        String resume = request.get("resume");
        String jd = request.get("job_description");
        Map result = aiService.analyzeResume(resume, jd);
        return ResponseEntity.ok(result);
    }

    // ── COVER LETTER ─────────────────────────────────────────
    @PostMapping("/cover-letter")
    public ResponseEntity<Map> coverLetter(@RequestBody Map<String, String> request) {
        String resume      = request.get("resume");
        String jd          = request.get("job_description");
        String companyName = request.get("company_name");
        String tone        = request.getOrDefault("tone", "professional");

        Map result = aiService.generateCoverLetter(resume, jd, companyName, tone);
        return ResponseEntity.ok(result);
    }
}