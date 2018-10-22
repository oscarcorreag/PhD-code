package unimelb.edu.au.ridesharing;

import android.content.Intent;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;

public class SessionActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_session);
    }

    public void createSession(View view) {
        Intent intent = new Intent(this, NewSessionActivity.class);
//        intent.putExtra("user", mSelectedUser);
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
