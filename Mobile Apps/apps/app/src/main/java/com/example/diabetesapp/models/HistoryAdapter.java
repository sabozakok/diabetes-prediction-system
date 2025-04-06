// HistoryAdapter.java
package com.example.diabetesapp;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;
import com.example.diabetesapp.models.PredictionRecord;

import java.util.List;

public class HistoryAdapter extends RecyclerView.Adapter<HistoryAdapter.ViewHolder> {

    private List<PredictionRecord> historyList;

    public HistoryAdapter(List<PredictionRecord> list) {
        this.historyList = list;
    }

    public static class ViewHolder extends RecyclerView.ViewHolder {
        TextView tvDate, tvSummary;

        public ViewHolder(View itemView) {
            super(itemView);
            tvDate = itemView.findViewById(R.id.tvDate);
            tvSummary = itemView.findViewById(R.id.tvSummary);
        }
    }

    @NonNull
    @Override
    public HistoryAdapter.ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View v = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.item_history, parent, false);
        return new ViewHolder(v);
    }

    @Override
    public void onBindViewHolder(@NonNull HistoryAdapter.ViewHolder holder, int position) {
        PredictionRecord record = historyList.get(position);
        holder.tvDate.setText(record.getCreatedAt());
        holder.tvSummary.setText("Risk: " + record.getProbability() + "% | Age: " + record.getAge());
    }

    @Override
    public int getItemCount() {
        return historyList.size();
    }
}
