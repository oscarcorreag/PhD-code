package unimelb.edu.au.ridesharing;

import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.widget.ListView;

import java.util.List;

import unimelb.edu.au.ridesharing.adapters.SessionsAdapter;
import unimelb.edu.au.ridesharing.model.Session;
import unimelb.edu.au.ridesharing.rest.SessionController;

public class ExistingSessionsActivity extends AppCompatActivity implements
        SessionController.SessionControllerListener {

    private static final String TAG = "ExistingSessionActivity";

    ListView mSessionsListView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_existing_sessions);

        mSessionsListView = findViewById(R.id.sessions_listView);

        SessionController sessionController = new SessionController(this);
        sessionController.getSessions();
    }

    @Override
    public void processSessions(List<Session> sessions) {
        SessionsAdapter sessionsAdapter = new SessionsAdapter(this, R.layout.item_session, sessions);
        mSessionsListView.setAdapter(sessionsAdapter);
    }
}
