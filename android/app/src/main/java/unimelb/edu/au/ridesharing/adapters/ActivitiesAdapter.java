package unimelb.edu.au.ridesharing.adapters;

import android.content.Context;
import android.support.annotation.NonNull;
import android.support.annotation.Nullable;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.ImageView;
import android.widget.RadioButton;
import android.widget.TextView;

import java.util.List;

import unimelb.edu.au.ridesharing.R;
import unimelb.edu.au.ridesharing.model.Activity;
import unimelb.edu.au.ridesharing.model.SessionActivity;

public class ActivitiesAdapter extends ArrayAdapter<SessionActivity> {

    private final Context mContext;
    private final int mResource;
    private final List<SessionActivity> mActivities;

    public ActivitiesAdapter(@NonNull Context context, int resource, @NonNull List<SessionActivity> activities) {
        super(context, resource, activities);

        mContext = context;
        mResource = resource;
        mActivities = activities;
    }

    public interface OnSelectRadioButtonClickListener {
        void onClick(View v, SessionActivity activity);
    }

    private OnSelectRadioButtonClickListener mOnSelectRadioButtonClickListener;

    public void setOnSelectRadioButtonClickListener(OnSelectRadioButtonClickListener listener) {
        this.mOnSelectRadioButtonClickListener = listener;
    }


    @NonNull
    @Override
    public View getView(int position, @Nullable View convertView, @NonNull ViewGroup parent) {

        View view = convertView;

        if (view == null) {
            view = LayoutInflater.from(mContext).inflate(mResource, parent, false);
        }

        SessionActivity sessionActivity = mActivities.get(position);
        Activity activity = Activity.fromValue(sessionActivity.getActivity());

        ImageView activityImageView = view.findViewById(R.id.activity_imageView);
        activityImageView.setImageResource(activity.getResourceId());

        TextView activityTextView = view.findViewById(R.id.activity_textView);
        activityTextView.setText(activity.getName());

        RadioButton selectActivityRadioButton = view.findViewById(R.id.select_activity_radioButton);
        selectActivityRadioButton.setTag(sessionActivity);
        selectActivityRadioButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                SessionActivity a = (SessionActivity) v.getTag();
                mOnSelectRadioButtonClickListener.onClick(v, a);
            }
        });

        return view;
    }
}
