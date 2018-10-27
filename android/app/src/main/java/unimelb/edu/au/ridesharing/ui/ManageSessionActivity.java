package unimelb.edu.au.ridesharing.ui;

import android.content.Intent;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.view.View;
import android.widget.ProgressBar;
import android.widget.Toast;

import org.json.JSONObject;

import unimelb.edu.au.ridesharing.R;
import unimelb.edu.au.ridesharing.ResponseStatus;
import unimelb.edu.au.ridesharing.model.Session;
import unimelb.edu.au.ridesharing.model.SessionUser;
import unimelb.edu.au.ridesharing.model.User;
import unimelb.edu.au.ridesharing.rest.SessionController;

public class ManageSessionActivity extends AppCompatActivity implements
        SessionController.CanCreateSessionControllerListener,
        SessionController.JoinSessionControllerListener {

    private static final String TAG = "ManageSessionActivity";

    User mSelectedUser;
    SessionController mSessionController;
    ProgressBar mProgressBar;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_session);

        mSelectedUser = getIntent().getParcelableExtra("user");

        mSessionController = new SessionController();
        mSessionController.setJoinSessionListener(this);
        mSessionController.setCanCreateSessionListener(this);

        mProgressBar = findViewById(R.id.join_progressBar);
    }

    public void createSession(View view) {
        mProgressBar.setVisibility(View.VISIBLE);
        mSessionController.canCreate();
    }

    public void joinSession(View view) {
        mProgressBar.setVisibility(View.VISIBLE);
        mSessionController.joinSession(mSelectedUser.getId());
    }

    public void endSession(View view) {
    }

    @Override
    public void processActiveSession(Session session, ResponseStatus responseStatus) {

        mProgressBar.setVisibility(View.GONE);

        if (responseStatus.isSuccessful()) {
            Toast.makeText(this, responseStatus.getDetail(), Toast.LENGTH_LONG).show();

            SessionUser sessionUser = new SessionUser(session.getId(), mSelectedUser.getId());
            sessionUser.setSession(session);
            sessionUser.setUser(mSelectedUser);

            Intent intent = new Intent(this, ActivityListActivity.class);
            intent.putExtra("sessionUser", sessionUser);
            startActivity(intent);
        } else {
            showErrorFragment(responseStatus.getDetail());
        }
    }

    @Override
    public void processResponse(ResponseStatus responseStatus) {

        mProgressBar.setVisibility(View.GONE);

        if (responseStatus.isSuccessful()) {
//            Toast.makeText(this, responseStatus.getDetail(), Toast.LENGTH_LONG).show();
            Intent intent = new Intent(this, NewSessionActivity.class);
            intent.putExtra("user", mSelectedUser);
            startActivity(intent);
        } else {
            showErrorFragment(responseStatus.getDetail());
        }
    }

    private void showErrorFragment(String message) {
        ErrorDialogFragment errorDialogFragment = new ErrorDialogFragment();
        Bundle args = new Bundle();
        args.putCharSequence("message", message);
        errorDialogFragment.setArguments(args);
        errorDialogFragment.show(getSupportFragmentManager(), "ErrorDialogFragment");
    }
}
