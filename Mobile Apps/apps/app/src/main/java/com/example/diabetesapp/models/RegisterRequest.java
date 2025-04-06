// RegisterRequest.java
package com.example.diabetesapp.models;

public class RegisterRequest {
    private String full_name;
    private String phone;
    private String email;
    private String username;
    private String password;
    private String role;

    public RegisterRequest(String full_name, String phone, String email, String username, String password, String role) {
        this.full_name = full_name;
        this.phone = phone;
        this.email = email;
        this.username = username;
        this.password = password;
        this.role = role;
    }
}
