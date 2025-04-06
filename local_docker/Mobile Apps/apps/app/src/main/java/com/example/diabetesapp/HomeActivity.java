// HomeActivity.java
package com.example.diabetesapp;

import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.widget.*;
import androidx.appcompat.app.AppCompatActivity;

public class HomeActivity extends AppCompatActivity {

    TextView tvWelcome;
    Button btnPredict, btnHistory, btnLogout;
    int userId;
    String username;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_home); // or R.layout.content_main if you use that

        // Bind views
        tvWelcome = findViewById(R.id.tvWelcome);
        btnPredict = findViewById(R.id.btnPredict);
        btnHistory = findViewById(R.id.btnHistory);
        btnLogout = findViewById(R.id.btnLogout);

        // Get user session
        SharedPreferences sp = getSharedPreferences("UserSession", MODE_PRIVATE);
        username = sp.getString("username", "User");
        userId = sp.getInt("user_id", -1);

        // Redirect if session not found
        if (userId == -1) {
            startActivity(new Intent(this, LoginActivity.class));
            finish();
            return;
        }

        tvWelcome.setText("Welcome, " + username + " (ID: " + userId + ")");

        // Set button actions
        btnPredict.setOnClickListener(v -> {
            Intent i = new Intent(HomeActivity.this, PredictorActivity.class);
            i.putExtra("user_id", userId);
            startActivity(i);
        });

        btnHistory.setOnClickListener(v -> {
            Intent i = new Intent(HomeActivity.this, HistoryActivity.class);
            i.putExtra("user_id", userId);
            startActivity(i);
        });

        btnLogout.setOnClickListener(v -> {
            SharedPreferences.Editor editor = sp.edit();
            editor.clear();
            editor.apply();

            Toast.makeText(this, "Logged out", Toast.LENGTH_SHORT).show();
            startActivity(new Intent(HomeActivity.this, LoginActivity.class));
            finish();
        });
    }
}
