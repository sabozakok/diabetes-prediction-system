// PredictRequest.java
package com.example.diabetesapp.models;

public class PredictRequest {
    private int user_Id;
    private float Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin, BMI, DiabetesPedigree;
    private int Age;

    public PredictRequest(int user_Id, float Pregnancies, float Glucose, float BloodPressure,
                          float SkinThickness, float Insulin, float BMI,
                          float DiabetesPedigree, int Age) {
        this.user_Id = user_Id;
        this.Pregnancies = Pregnancies;
        this.Glucose = Glucose;
        this.BloodPressure = BloodPressure;
        this.SkinThickness = SkinThickness;
        this.Insulin = Insulin;
        this.BMI = BMI;
        this.DiabetesPedigree = DiabetesPedigree;
        this.Age = Age;
    }
}
