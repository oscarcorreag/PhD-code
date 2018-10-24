package unimelb.edu.au.ridesharing.ui;

import android.content.Intent;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;

import unimelb.edu.au.ridesharing.R;
import unimelb.edu.au.ridesharing.model.User;
import unimelb.edu.au.ridesharing.ui.ExistingSessionsActivity;
import unimelb.edu.au.ridesharing.ui.NewSessionActivity;

public class ManageSessionActivity extends AppCompatActivity {

    private static final String TAG = "SessionActivity";

    User mSelectedUser;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_session);

        mSelectedUser = getIntent().getParcelableExtra("user");
    }

    public void createSession(View view) {
        Intent intent = new Intent(this, NewSessionActivity.class);
        intent.putExtra("user", mSelectedUser);
        startActivity(intent);
    }

    public void joinSession(View view) {
        Intent intent = new Intent(this, ExistingSessionsActivity.class);
//        intent.putExtra("user", mSelectedUser);
        startActivity(intent);
    }

    public void endSession(View view) {
    }
}
