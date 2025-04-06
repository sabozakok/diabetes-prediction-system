// PredictionRecord.java
package com.example.diabetesapp.models;

public class PredictionRecord {
    private int patient_id;
    private String created_at;
    private float glucose, bmi, probability;
    private int age;

    public int getPatientId() { return patient_id; }
    public String getCreatedAt() { return created_at; }
    public float getGlucose() { return glucose; }
    public float getBmi() { return bmi; }
    public float getProbability() { return probability; }
    public int getAge() { return age; }
}
