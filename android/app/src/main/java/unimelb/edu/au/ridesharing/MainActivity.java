package unimelb.edu.au.ridesharing;

import android.content.Intent;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Spinner;

import java.util.List;

import unimelb.edu.au.ridesharing.model.User;
import unimelb.edu.au.ridesharing.rest.UserController;

public class MainActivity extends AppCompatActivity implements
        UserController.UserControllerListener,
        AdapterView.OnItemSelectedListener {

    Spinner mSpinner;
    User mSelectedUser;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        mSpinner = findViewById(R.id.user_spinner);

        UserController userController = new UserController(this);
        userController.getUsers();
    }

    @Override
    public void processUsers(List<User> users) {
        ArrayAdapter<User> userAdapter = new ArrayAdapter<>(this, R.layout.support_simple_spinner_dropdown_item, users);
        mSpinner.setAdapter(userAdapter);
    }

    @Override
    public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {
        mSelectedUser = (User) parent.getItemAtPosition(position);
    }

    @Override
    public void onNothingSelected(AdapterView<?> parent) {

    }

    public void manageSession(View view) {
        Intent intent = new Intent(this, SessionActivity.class);
        intent.putExtra("user", mSelectedUser);
        startActivity(intent);
    }
}
