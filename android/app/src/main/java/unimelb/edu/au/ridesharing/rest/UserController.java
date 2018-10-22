package unimelb.edu.au.ridesharing.rest;

import android.support.annotation.NonNull;
import android.util.Log;

import java.io.IOException;
import java.util.List;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;
import unimelb.edu.au.ridesharing.model.User;

public class UserController implements Callback<List<User>> {

    private static final String TAG = "UserController";

    public interface UserControllerListener {
        void processUsers(List<User> users);
    }

    private UserControllerListener mListener;

    public UserController(UserControllerListener listener) {
        mListener = listener;
    }

    public void getUsers() {
        Call<List<User>> call = RsRestService.getInstance().getService().getUsers();
        call.enqueue(this);
    }

    @Override
    public void onResponse(@NonNull Call<List<User>> call, @NonNull Response<List<User>> response) {
        if (response.isSuccessful()) {
            List<User> users = response.body();
            mListener.processUsers(users);
        } else {
            try {
                Log.e(TAG, response.errorBody().string());
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }

    @Override
    public void onFailure(@NonNull Call<List<User>> call, @NonNull Throwable t) {
        Log.e(TAG, t.getLocalizedMessage());
    }
}
