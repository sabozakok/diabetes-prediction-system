// FileUtils.java
package com.example.diabetesapp.utils;

import java.io.*;

public class FileUtils {

    public static String readUrlFromFile(String filePath) {
        StringBuilder content = new StringBuilder();
        try {
            File file = new File(filePath);
            BufferedReader br = new BufferedReader(new FileReader(file));
            String line;
            while ((line = br.readLine()) != null) {
                content.append(line);
            }
            br.close();
            return content.toString().trim(); // Remove extra spaces
        } catch (IOException e) {
            e.printStackTrace();
            return null;
        }
    }
}

