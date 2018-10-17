package unimelb.edu.au.ridesharing;

import android.content.Intent;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.ListView;

import java.util.ArrayList;

import unimelb.edu.au.ridesharing.model.Activity;

public class ActivityListActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_activities);
        populateActivities();
    }

    private void populateActivities() {
        ArrayList<Activity> activities = new ActivityManager(this).load();
        ActivityListViewAdapter adapter = new ActivityListViewAdapter(this, R.layout.item_activity, activities);
        ListView lvActivities = findViewById(R.id.lv_activities);
        lvActivities.setAdapter(adapter);
    }

    public void showOrigins(View view)
    {
        Intent intent = new Intent(ActivityListActivity.this, OriginsActivity.class);
        startActivity(intent);
    }
}
