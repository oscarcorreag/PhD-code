package unimelb.edu.au.ridesharing.ui;

import android.content.Intent;
import android.os.Bundle;
import android.support.annotation.NonNull;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.ProgressBar;
import android.widget.Spinner;
import android.widget.Toast;

import com.google.android.gms.tasks.OnCompleteListener;
import com.google.android.gms.tasks.Task;
import com.google.firebase.iid.FirebaseInstanceId;
import com.google.firebase.iid.InstanceIdResult;

import java.util.List;

import unimelb.edu.au.ridesharing.R;
import unimelb.edu.au.ridesharing.ResponseStatus;
import unimelb.edu.au.ridesharing.model.User;
import unimelb.edu.au.ridesharing.rest.UserController;

public class MainActivity extends AppCompatActivity implements
        UserController.UserControllerListener {

    private static final String TAG = MainActivity.class.getName();

    Spinner mUsersSpinner;
    ProgressBar mUsersProgressBar;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        mUsersSpinner = findViewById(R.id.user_spinner);

        UserController userController = new UserController();
        userController.setListener(this);
        userController.getUsers();

        mUsersProgressBar = findViewById(R.id.users_progressBar);
        mUsersProgressBar.setVisibility(View.VISIBLE);
    }

    @Override
    public void processUsers(List<User> users, ResponseStatus responseStatus) {

        mUsersProgressBar.setVisibility(View.GONE);

        if (responseStatus.isSuccessful()) {
            ArrayAdapter<User> userAdapter =
                    new ArrayAdapter<>(
                            this,
                            R.layout.support_simple_spinner_dropdown_item,
                            users);
            mUsersSpinner.setAdapter(userAdapter);
        } else {
            MsgDialogFragment msgDialogFragment = new MsgDialogFragment();
            Bundle args = new Bundle();
            args.putCharSequence("message", responseStatus.getDetail());
            msgDialogFragment.setArguments(args);
            msgDialogFragment.show(getSupportFragmentManager(), "MsgDialogFragment");
        }

    }

    public void manageSession(View view) {

        FirebaseInstanceId.getInstance().getInstanceId()
                .addOnCompleteListener(new OnCompleteListener<InstanceIdResult>() {
                    @Override
                    public void onComplete(@NonNull Task<InstanceIdResult> task) {
                        if (!task.isSuccessful()) {
                            Log.w(TAG, "getInstanceId failed", task.getException());
                            return;
                        }
                        // Get new Instance ID token
                        String token = task.getResult().getToken();

                        // Log and toast
                        String msg = String.format("InstanceID Token: %s", token);
                        Log.d(TAG, msg);
                        Toast.makeText(MainActivity.this, msg, Toast.LENGTH_SHORT).show();
                    }
                });

        Intent intent = new Intent(this, ManageSessionActivity.class);
        intent.putExtra("user", (User) mUsersSpinner.getSelectedItem());
        startActivity(intent);
    }
}
