package unimelb.edu.au.ridesharing;

import android.content.Context;
import android.content.res.TypedArray;

import java.util.ArrayList;

public class ActivityManager {

    private Context context;

    ActivityManager(Context context) {
        this.context = context;
    }

    public ArrayList<Activity> load() {
        ArrayList<Activity> activities = new ArrayList<Activity>();
        int[] ids = context.getResources().getIntArray(R.array.activity_ids);
        String[] names = context.getResources().getStringArray(R.array.activities);
        TypedArray icons = context.getResources().obtainTypedArray(R.array.activities_icons);
        for (int i = 0; i < ids.length; i++) {
            Activity activity = new Activity(ids[i], names[i], icons.getResourceId(i, 0));
            activities.add(activity);
        }
        icons.recycle();
        return activities;
    }
}
