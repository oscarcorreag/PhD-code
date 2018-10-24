package unimelb.edu.au.ridesharing.adapters;

import android.content.Context;
import android.content.res.TypedArray;

import java.util.ArrayList;

import unimelb.edu.au.ridesharing.R;
import unimelb.edu.au.ridesharing.model.SessionActivity;

public class ActivityManager {

    private Context context;

    ActivityManager(Context context) {
        this.context = context;
    }

    public ArrayList<SessionActivity> load() {
        ArrayList<SessionActivity> activities = new ArrayList<SessionActivity>();
        int[] ids = context.getResources().getIntArray(R.array.activity_ids);
        String[] names = context.getResources().getStringArray(R.array.activities);
        TypedArray icons = context.getResources().obtainTypedArray(R.array.activities_icons);
//        for (int i = 0; i < ids.length; i++) {
//            SessionActivity sessionActivity = new SessionActivity(ids[i], names[i], icons.getResourceId(i, 0));
//            activities.add(sessionActivity);
//        }
        icons.recycle();
        return activities;
    }
}
