// HistoryActivity.java
package com.example.diabetesapp;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.*;
import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.example.diabetesapp.api.ApiClient;
import com.example.diabetesapp.api.ApiService;
import com.example.diabetesapp.models.HistoryResponse;
import com.example.diabetesapp.models.PredictionRecord;

import java.util.ArrayList;
import java.util.List;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class HistoryActivity extends AppCompatActivity {

    RecyclerView recyclerView;
    ProgressBar progressBar;
    TextView tvNoData;

    int userId;
    ApiService apiService;
    HistoryAdapter adapter;
    List<PredictionRecord> userRecords = new ArrayList<>();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_history);

        // Bind views
        recyclerView = findViewById(R.id.recyclerHistory);
        progressBar = findViewById(R.id.progressBar);
        tvNoData = findViewById(R.id.tvNoData);

        // Setup RecyclerView
        recyclerView.setLayoutManager(new LinearLayoutManager(this));
        adapter = new HistoryAdapter(userRecords);
        recyclerView.setAdapter(adapter);

        // Get user ID
        userId = getIntent().getIntExtra("user_id", -1);
        if (userId == -1) {
            startActivity(new Intent(this, LoginActivity.class));
            finish();
            return;
        }

        apiService = ApiClient.getClient().create(ApiService.class);
        loadHistory();
    }

    private void loadHistory() {
        progressBar.setVisibility(View.VISIBLE);

        apiService.getHistory().enqueue(new Callback<HistoryResponse>() {
            @Override
            public void onResponse(Call<HistoryResponse> call, Response<HistoryResponse> response) {
                progressBar.setVisibility(View.GONE);

                if (response.isSuccessful() && response.body() != null && response.body().isSuccess()) {
                    List<PredictionRecord> allRecords = response.body().getHistory();

                    userRecords.clear();
                    for (PredictionRecord record : allRecords) {
                        if (record.getPatientId() == userId) {
                            userRecords.add(record);
                        }
                    }

                    adapter.notifyDataSetChanged();
                    tvNoData.setVisibility(userRecords.isEmpty() ? View.VISIBLE : View.GONE);
                } else {
                    Toast.makeText(HistoryActivity.this, "No history found", Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onFailure(Call<HistoryResponse> call, Throwable t) {
                progressBar.setVisibility(View.GONE);
                Toast.makeText(HistoryActivity.this, "Error: " + t.getMessage(), Toast.LENGTH_SHORT).show();
            }
        });
    }
}
