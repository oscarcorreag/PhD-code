package unimelb.edu.au.ridesharing.ui;

import android.content.Intent;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.EditText;
import android.widget.ProgressBar;
import android.widget.Spinner;
import android.widget.Toast;

import unimelb.edu.au.ridesharing.R;
import unimelb.edu.au.ridesharing.ResponseStatus;
import unimelb.edu.au.ridesharing.model.City;
import unimelb.edu.au.ridesharing.model.Session;
import unimelb.edu.au.ridesharing.model.SessionUser;
import unimelb.edu.au.ridesharing.model.User;
import unimelb.edu.au.ridesharing.rest.SessionController;

public class NewSessionActivity extends AppCompatActivity implements SessionController.NewSessionControllerListener {

    private static final String TAG = "NewSessionActivity";

    User mSelectedUser;
    Spinner mCitiesSpinner;
    ProgressBar mCreateProgressBar;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_new_session);

        mSelectedUser = getIntent().getParcelableExtra("user");

        mCitiesSpinner = findViewById(R.id.city_spinner);
        mCreateProgressBar = findViewById(R.id.create_progressBar);

        ArrayAdapter<City> adapter =
                new ArrayAdapter<>(
                        this,
                        R.layout.support_simple_spinner_dropdown_item,
                        City.values());

        mCitiesSpinner.setAdapter(adapter);
    }

    public void createSession(View view) {

        mCreateProgressBar.setVisibility(View.VISIBLE);

        // TODO: Validate input.

        City city = (City) mCitiesSpinner.getSelectedItem();

        EditText realUsersEditText = findViewById(R.id.real_users_editText);
        int realUsers = Integer.parseInt(realUsersEditText.getText().toString());

        EditText simulatedUsersEditText = findViewById(R.id.simulated_users_editText);
        int simulatedUsers = Integer.parseInt(simulatedUsersEditText.getText().toString());

        Session session = new Session(city.getIataCode(), mSelectedUser.getId(), realUsers, simulatedUsers);

        SessionController sessionController = new SessionController();
        sessionController.setNewSessionListener(this);
        sessionController.postSession(session);
    }

    @Override
    public void processNewSession(Session session, ResponseStatus responseStatus) {

        mCreateProgressBar.setVisibility(View.GONE);

        if (responseStatus.isSuccessful()) {
            Toast.makeText(this, responseStatus.getDetail(), Toast.LENGTH_LONG).show();

            SessionUser sessionUser = new SessionUser(session.getId(), mSelectedUser.getId());
            sessionUser.setSession(session);
            sessionUser.setUser(mSelectedUser);

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
