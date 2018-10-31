package unimelb.edu.au.ridesharing.ui;

import android.Manifest;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.os.Bundle;
import android.preference.PreferenceManager;
import android.support.annotation.NonNull;
import android.support.v4.app.ActivityCompat;
import android.support.v7.app.AppCompatActivity;
import android.telephony.TelephonyManager;
import android.util.Log;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.ProgressBar;
import android.widget.Spinner;

import com.google.android.gms.tasks.OnCompleteListener;
import com.google.android.gms.tasks.Task;
import com.google.firebase.iid.FirebaseInstanceId;
import com.google.firebase.iid.InstanceIdResult;

import java.util.List;

import unimelb.edu.au.ridesharing.R;
import unimelb.edu.au.ridesharing.ResponseStatus;
import unimelb.edu.au.ridesharing.model.User;
import unimelb.edu.au.ridesharing.rest.FcmController;
import unimelb.edu.au.ridesharing.rest.UserController;

public class MainActivity extends AppCompatActivity implements
        UserController.UserControllerListener,
        OnCompleteListener<InstanceIdResult>,
        FcmController.RegistrationFcmControllerListener {

    private static final String TAG = MainActivity.class.getName();

    User mSelectedUser;
    Spinner mUsersSpinner;
    ProgressBar mUsersProgressBar;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        mUsersSpinner = findViewById(R.id.user_spinner);

        UserController userController = new UserController();
        userController.setListener(this);
        userController.getUsers("admin");

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
        mSelectedUser = (User) mUsersSpinner.getSelectedItem();
        FirebaseInstanceId.getInstance().getInstanceId().addOnCompleteListener(this);
    }

    @Override
    public void processResponseRegistration(ResponseStatus responseStatus) {
        if (responseStatus.isSuccessful()) {
            Intent intent = new Intent(this, ManageSessionActivity.class);
            intent.putExtra("user", mSelectedUser);
            startActivity(intent);
        } else {
            Log.e(TAG, responseStatus.getDetail());
        }
    }

    @Override
    public void onComplete(@NonNull Task<InstanceIdResult> task) {
        if (!task.isSuccessful()) {
            Log.w(TAG, "getInstanceId failed", task.getException());
            return;
        }
        // Get new Instance ID token
        String token = task.getResult().getToken();

//        // Check whether token has changed.
//        SharedPreferences sharedPreferences = PreferenceManager.getDefaultSharedPreferences(this);
//        String tokenStored = sharedPreferences.getString("token", "");
//
//        if (token.equals(tokenStored)) {
//
//            Intent intent = new Intent(this, ManageSessionActivity.class);
//            intent.putExtra("user", mSelectedUser);
//            startActivity(intent);
//
//            return;
//        }

        // Send token to the App Server.
        FcmController fcmController = new FcmController();
        fcmController.setRegistrationFcmListener(this);
        TelephonyManager telephonyManager = (TelephonyManager) getSystemService(Context.TELEPHONY_SERVICE);
        if (ActivityCompat.checkSelfPermission(this, Manifest.permission.READ_PHONE_STATE) != PackageManager.PERMISSION_GRANTED) {
            // TODO: Consider calling
            //    ActivityCompat#requestPermissions
            // here to request the missing permissions, and then overriding
            //   public void onRequestPermissionsResult(int requestCode, String[] permissions,
            //                                          int[] grantResults)
            // to handle the case where the user grants the permission. See the documentation
            // for ActivityCompat#requestPermissions for more details.
            return;
        }
        fcmController.sendRegistrationToServer(mSelectedUser.getUsername(), token, telephonyManager.getDeviceId());
    }
}
