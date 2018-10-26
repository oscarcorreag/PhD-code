package unimelb.edu.au.ridesharing.ui;

import android.content.Intent;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.view.View;
import android.widget.ProgressBar;
import android.widget.Toast;

import unimelb.edu.au.ridesharing.R;
import unimelb.edu.au.ridesharing.ResponseStatus;
import unimelb.edu.au.ridesharing.model.Session;
import unimelb.edu.au.ridesharing.model.SessionUser;
import unimelb.edu.au.ridesharing.model.User;
import unimelb.edu.au.ridesharing.rest.SessionController;

public class ManageSessionActivity extends AppCompatActivity implements SessionController.JoinSessionControllerListener {

    private static final String TAG = "ManageSessionActivity";

    User mSelectedUser;
    ProgressBar mJoinProgressBar;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_session);

        mSelectedUser = getIntent().getParcelableExtra("user");

        mJoinProgressBar = findViewById(R.id.join_progressBar);
    }

    public void createSession(View view) {
        // TODO: Check first whether there is already an active session.
        Intent intent = new Intent(this, NewSessionActivity.class);
        intent.putExtra("user", mSelectedUser);
        startActivity(intent);
    }

    public void joinSession(View view) {

        mJoinProgressBar.setVisibility(View.VISIBLE);

        SessionController sessionController = new SessionController();
        sessionController.setJoinSessionListener(this);
        sessionController.joinSession(mSelectedUser.getId());
    }

    public void endSession(View view) {
    }

    @Override
    public void processActiveSession(Session session, ResponseStatus responseStatus) {

        mJoinProgressBar.setVisibility(View.GONE);

        if (responseStatus.isSuccessful()) {
            Toast.makeText(this, responseStatus.getDetail(), Toast.LENGTH_LONG).show();

            SessionUser sessionUser = new SessionUser(session.getId(), mSelectedUser.getId());

            Intent intent = new Intent(this, ActivityListActivity.class);
            intent.putExtra("sessionUser", sessionUser);
            startActivity(intent);
        } else {
            ErrorDialogFragment errorDialogFragment = new ErrorDialogFragment();
            Bundle args = new Bundle();
            args.putCharSequence("message", responseStatus.getDetail());
            errorDialogFragment.setArguments(args);
            errorDialogFragment.show(getSupportFragmentManager(), "ErrorDialogFragment");
        }
    }
}
