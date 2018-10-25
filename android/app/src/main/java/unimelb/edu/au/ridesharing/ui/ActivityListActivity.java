package unimelb.edu.au.ridesharing.ui;

import unimelb.edu.au.ridesharing.R;
import unimelb.edu.au.ridesharing.ResponseStatus;
import unimelb.edu.au.ridesharing.adapters.ActivitiesAdapter;
import unimelb.edu.au.ridesharing.model.Session;
import unimelb.edu.au.ridesharing.model.SessionActivity;
import unimelb.edu.au.ridesharing.rest.SessionActivityController;

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

    Session mSession;
    ListView mActivitiesListView;
    ProgressBar mActivitiesProgressBar;
    RadioButton mSelectRadioButton = null;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_list);

        mSession = getIntent().getParcelableExtra("session");

        mActivitiesListView = findViewById(R.id.activities_listView);

        SessionActivityController sessionActivityController = new SessionActivityController();
        sessionActivityController.setActivityListListener(this);
        sessionActivityController.getActivities(mSession.getId());

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
            ErrorDialogFragment errorDialogFragment = new ErrorDialogFragment();
            Bundle args = new Bundle();
            args.putCharSequence("message", responseStatus.getDetail());
            errorDialogFragment.setArguments(args);
            errorDialogFragment.show(getSupportFragmentManager(), "ErrorDialogFragment");
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
}
