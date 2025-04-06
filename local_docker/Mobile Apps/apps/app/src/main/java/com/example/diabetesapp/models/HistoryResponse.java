// HistoryResponse.java
package com.example.diabetesapp.models;

import java.util.List;

public class HistoryResponse {
    private boolean success;
    private List<PredictionRecord> history;

    public boolean isSuccess() { return success; }
    public List<PredictionRecord> getHistory() { return history; }
}


