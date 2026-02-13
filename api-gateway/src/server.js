import express from 'express';

const app = express();

const PORT = process.env.PORT || 3000;

const ragServiceBaseUrl = process.env.RAG_SERVICE_BASE_URL || "http://localhost:8000";

// Middleware to parse JSON bodies
app.use(express.json());

// Health check endpoint
app.get("/health", (req, res) =>{
    res.status(200).json({
        status: "ok",
        service: "api-gateway",
    });
});

// Proxy health check to rag-service
app.get("/v1/rag/health", async (_req, res) => {
    const response = await fetch(`${ragServiceBaseUrl}/health`);
    const data = await response.json();

    res.status(200).json({
        gateway: {status: "ok", service: "api-gateway"},
        ragService: data
    });
});

// Start HTTP server
app.listen(PORT, () => {
    console.log(`api-gateway running on port ${PORT}`);
});