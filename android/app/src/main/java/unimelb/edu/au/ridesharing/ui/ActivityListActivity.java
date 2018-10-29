package unimelb.edu.au.ridesharing.ui;

import unimelb.edu.au.ridesharing.R;
import unimelb.edu.au.ridesharing.ResponseStatus;
import unimelb.edu.au.ridesharing.adapters.ActivitiesAdapter;
import unimelb.edu.au.ridesharing.model.SessionActivity;
import unimelb.edu.au.ridesharing.model.SessionUser;
import unimelb.edu.au.ridesharing.rest.SessionActivityController;

import android.content.Intent;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.ListView;
import android.widget.ProgressBar;
import android.widget.RadioButton;

import java.util.List;

public class ActivityListActivity extends AppCompatActivity implements
        SessionActivityController.ActivityListControllerListener,
        ActivitiesAdapter.OnSelectRadioButtonClickListener{

    private static final String TAG = "ActivityListActivity";

    SessionUser mSessionUser;
    ListView mActivitiesListView;
    ProgressBar mActivitiesProgressBar;
    RadioButton mSelectRadioButton = null;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_list);

        mSessionUser = getIntent().getParcelableExtra("sessionUser");

        mActivitiesListView = findViewById(R.id.activities_listView);

        SessionActivityController sessionActivityController = new SessionActivityController();
        sessionActivityController.setActivityListListener(this);
        sessionActivityController.getActivities(mSessionUser.getSessionId());

        mActivitiesProgressBar = findViewById(R.id.activities_progressBar);
        mActivitiesProgressBar.setVisibility(View.VISIBLE);
    }

    @Override
    public void processActivities(List<SessionActivity> activities, ResponseStatus responseStatus) {

        mActivitiesProgressBar.setVisibility(View.GONE);

        if (responseStatus.isSuccessful()) {
            ActivitiesAdapter activitiesAdapter = new ActivitiesAdapter(this, R.layout.item_activity, activities);
            activitiesAdapter.setOnSelectRadioButtonClickListener(this);
            mActivitiesListView.setAdapter(activitiesAdapter);
        } else {
            showErrorFragment(responseStatus.getDetail());
        }
    }

    @Override
    public void onClick(View v, SessionActivity activity) {
        Log.d(TAG, activity.getActivity());

        if (mSelectRadioButton != null) {
            mSelectRadioButton.setChecked(false);
        }
        mSelectRadioButton = (RadioButton) v;
    }

    public void seeOrigins(View v) {
        if (mSelectRadioButton == null) {
            showErrorFragment("Choose an activity first.");
            return;
        }

        SessionActivity sessionActivity = (SessionActivity) mSelectRadioButton.getTag();

        Intent intent = new Intent(this, OriginActivity.class);
        intent.putExtra("sessionUser", mSessionUser);
        intent.putExtra("activity", sessionActivity.getActivity());
        startActivity(intent);
    }

    private void showErrorFragment(String message) {
        ErrorDialogFragment errorDialogFragment = new ErrorDialogFragment();
        Bundle args = new Bundle();
        args.putCharSequence("message", message);
        errorDialogFragment.setArguments(args);
        errorDialogFragment.show(getSupportFragmentManager(), "ErrorDialogFragment");
    }
}
