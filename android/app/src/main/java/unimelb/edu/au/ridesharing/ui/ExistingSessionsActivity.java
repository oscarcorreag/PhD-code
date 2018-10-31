package unimelb.edu.au.ridesharing.ui;

import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.widget.ListView;

import java.util.List;

import unimelb.edu.au.ridesharing.R;
import unimelb.edu.au.ridesharing.ResponseStatus;
import unimelb.edu.au.ridesharing.adapters.SessionsAdapter;
import unimelb.edu.au.ridesharing.model.Session;
import unimelb.edu.au.ridesharing.rest.SessionController;

public class ExistingSessionsActivity extends AppCompatActivity implements
        SessionController.SessionListControllerListener {

    private static final String TAG = "ExistingSessionActivity";

    ListView mSessionsListView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_existing_sessions);

        mSessionsListView = findViewById(R.id.sessions_listView);

        SessionController sessionController = new SessionController();
        sessionController.setSessionListListener(this);
        // TODO: Fix userName.
        sessionController.getSessions("admin");
    }

    @Override
    public void processSessions(List<Session> sessions, ResponseStatus responseStatus) {
        if (responseStatus.isSuccessful()) {
            SessionsAdapter sessionsAdapter = new SessionsAdapter(this, R.layout.item_session, sessions);
            mSessionsListView.setAdapter(sessionsAdapter);
        } else {
            MsgDialogFragment msgDialogFragment = new MsgDialogFragment();
            Bundle args = new Bundle();
            args.putCharSequence("message", responseStatus.getDetail());
            msgDialogFragment.setArguments(args);
            msgDialogFragment.show(getSupportFragmentManager(), "MsgDialogFragment");
        }
    }
}
