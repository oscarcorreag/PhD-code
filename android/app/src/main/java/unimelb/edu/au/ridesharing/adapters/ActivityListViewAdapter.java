package unimelb.edu.au.ridesharing.adapters;

import android.content.Context;
import android.support.annotation.NonNull;
import android.support.annotation.Nullable;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.ImageView;
import android.widget.TextView;

import java.util.List;

import unimelb.edu.au.ridesharing.R;
import unimelb.edu.au.ridesharing.model.SessionActivity;

public class ActivityListViewAdapter extends ArrayAdapter<SessionActivity> {

    ActivityListViewAdapter(@NonNull Context context, int resource, @NonNull List<SessionActivity> objects) {
        super(context, resource, objects);
    }

    @NonNull
    @Override
    public View getView(int position, @Nullable View convertView, @NonNull ViewGroup parent) {
        if (convertView == null) {
            convertView = LayoutInflater.from(getContext()).inflate(R.layout.item_activity, parent, false);
        }
        SessionActivity sessionActivity = getItem(position);

        ImageView imgActivity = convertView.findViewById(R.id.img_activity);
        TextView txtActivity = convertView.findViewById(R.id.txt_activity);
        if (sessionActivity != null) {
            imgActivity.setImageResource(sessionActivity.getResourceId());
            txtActivity.setText(sessionActivity.getName());
        }

        return convertView;
    }
}
