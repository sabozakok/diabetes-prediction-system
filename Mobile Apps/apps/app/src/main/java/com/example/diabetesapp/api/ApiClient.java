// ApiClient.java
package com.example.diabetesapp.api;

import retrofit2.Retrofit;
import retrofit2.converter.gson.GsonConverterFactory;
import android.os.Environment;
import com.example.diabetesapp.utils.FileUtils;

public class ApiClient {
    //private static final String BASE_URL = "http://192.168.100.187:5050/api/";
    private static Retrofit retrofit;

    public static Retrofit getClient() {
        if (retrofit == null) {

            String filePath = Environment.getExternalStorageDirectory() + "/Diabetes/diabetes_config.txt";
            String BASE_URL = FileUtils.readUrlFromFile(filePath);

            if (BASE_URL == null || !BASE_URL.startsWith("http")) {
                throw new RuntimeException("Invalid or missing BASE_URL in diabetes_config.txt");
            }

            retrofit = new Retrofit.Builder()
                    .baseUrl(BASE_URL)
                    .addConverterFactory(GsonConverterFactory.create())
                    .build();
        }
        return retrofit;
    }
}



