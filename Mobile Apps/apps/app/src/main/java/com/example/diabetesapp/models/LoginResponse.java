// LoginResponse.java
package com.example.diabetesapp.models;

public class LoginResponse {
    private String username;
    private String password;
    private boolean success;
    private int user_id;

    public LoginResponse(String username, String password) {
        this.username = username;
        this.password = password;
    }

    public boolean isSuccess() {
        return success;
    }

    public String getUsername() {
        return username;
    }

    public int getUserId() {
        return user_id;
    }
}
