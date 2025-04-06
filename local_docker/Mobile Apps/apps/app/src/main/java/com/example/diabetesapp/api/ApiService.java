// ApiService.java
package com.example.diabetesapp.api;

import com.example.diabetesapp.models.HistoryResponse;
import com.example.diabetesapp.models.LoginResponse;
import com.example.diabetesapp.models.PredictRequest;
import com.example.diabetesapp.models.PredictResponse;
import com.example.diabetesapp.models.RegisterRequest;


import java.util.List;

import retrofit2.Call;
import retrofit2.http.*;

public interface ApiService {

    @POST("login")
    Call<LoginResponse> login(@Body LoginResponse loginRequest);

    @POST("register")
    Call<Void> register(@Body RegisterRequest registerRequest);

    @POST("predict")
    Call<PredictResponse> predict(@Body PredictRequest predictRequest);

    @GET("history")
    Call<HistoryResponse> getHistory();
}
