// PredictorActivity.java
package com.example.diabetesapp;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.*;
import androidx.appcompat.app.AppCompatActivity;

import com.example.diabetesapp.api.ApiClient;
import com.example.diabetesapp.api.ApiService;
import com.example.diabetesapp.models.PredictRequest;
import com.example.diabetesapp.models.PredictResponse;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class PredictorActivity extends AppCompatActivity {

    EditText etPregnancies, etGlucose, etBP, etSkin, etInsulin, etBMI, etDPF, etAge;
    Button btnPredict;
    TextView tvResult;
    ProgressBar progressBar;

    int userId;
    ApiService apiService;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_predictor);

        etPregnancies = findViewById(R.id.etPregnancies);
        etGlucose = findViewById(R.id.etGlucose);
        etBP = findViewById(R.id.etBP);
        etSkin = findViewById(R.id.etSkin);
        etInsulin = findViewById(R.id.etInsulin);
        etBMI = findViewById(R.id.etBMI);
        etDPF = findViewById(R.id.etDPF);
        etAge = findViewById(R.id.etAge);
        btnPredict = findViewById(R.id.btnPredict);
        tvResult = findViewById(R.id.tvResult);
        progressBar = findViewById(R.id.progressBar);

        apiService = ApiClient.getClient().create(ApiService.class);

        userId = getIntent().getIntExtra("user_id", -1);
        if (userId == -1) {
            startActivity(new Intent(this, LoginActivity.class));
            finish();
        }

        btnPredict.setOnClickListener(v -> predictDiabetes());
    }

    private void predictDiabetes() {
        float pregnancies = Float.parseFloat(etPregnancies.getText().toString());
        float glucose = Float.parseFloat(etGlucose.getText().toString());
        float bp = Float.parseFloat(etBP.getText().toString());
        float skin = Float.parseFloat(etSkin.getText().toString());
        float insulin = Float.parseFloat(etInsulin.getText().toString());
        float bmi = Float.parseFloat(etBMI.getText().toString());
        float dpf = Float.parseFloat(etDPF.getText().toString());
        int age = Integer.parseInt(etAge.getText().toString());

        PredictRequest request = new PredictRequest(userId, pregnancies, glucose, bp, skin, insulin, bmi, dpf, age);

        progressBar.setVisibility(View.VISIBLE);

        apiService.predict(request).enqueue(new Callback<PredictResponse>() {
            @Override
            public void onResponse(Call<PredictResponse> call, Response<PredictResponse> response) {
                progressBar.setVisibility(View.GONE);
                if (response.isSuccessful() && response.body() != null) {
                    float probability = response.body().getProbability();
                    tvResult.setText("Diabetes Risk: " + probability + "%");
                    tvResult.setVisibility(View.VISIBLE);
                } else {
                    tvResult.setText("Prediction failed.");
                    tvResult.setVisibility(View.VISIBLE);
                }
            }

            @Override
            public void onFailure(Call<PredictResponse> call, Throwable t) {
                progressBar.setVisibility(View.GONE);
                tvResult.setText("Error: " + t.getMessage());
                tvResult.setVisibility(View.VISIBLE);
            }
        });
    }
}
