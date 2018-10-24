package unimelb.edu.au.ridesharing;

import android.content.Intent;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.Spinner;

import java.util.List;

import unimelb.edu.au.ridesharing.model.User;
import unimelb.edu.au.ridesharing.rest.UserController;

public class MainActivity extends AppCompatActivity implements
        UserController.UserControllerListener {

    private static final String TAG = "MainActivity";

    Spinner mUsersSpinner;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        mUsersSpinner = findViewById(R.id.user_spinner);

        UserController userController = new UserController(this);
        userController.getUsers();
    }

    @Override
    public void processUsers(List<User> users) {
        ArrayAdapter<User> userAdapter =
                new ArrayAdapter<>(
                        this,
                        R.layout.support_simple_spinner_dropdown_item,
                        users);
        mUsersSpinner.setAdapter(userAdapter);
    }

    public void manageSession(View view) {
        Intent intent = new Intent(this, SessionActivity.class);
        intent.putExtra("user", (User) mUsersSpinner.getSelectedItem());
        startActivity(intent);
    }
}
