package unimelb.edu.au.ridesharing.rest;

import android.support.annotation.NonNull;
import android.util.Log;

import java.io.IOException;
import java.util.List;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;
import unimelb.edu.au.ridesharing.ResponseStatus;
import unimelb.edu.au.ridesharing.model.User;

public class UserController {

    private static final String TAG = "UserController";
    private static final StatusCode DEFAULT_STATUS_CODE = StatusCode.INTERNAL_SERVER_ERROR;

    public interface UserControllerListener {
        void processUsers(List<User> users, ResponseStatus status);
    }

    private UserControllerListener mListener;

    public void setListener(UserControllerListener listener) {
        this.mListener = listener;
    }

    public void getUsers() {
        Call<List<User>> call = RsRestService.getInstance().getService().getUsers();
        call.enqueue(new Callback<List<User>>() {
            @Override
            public void onResponse(@NonNull Call<List<User>> call, @NonNull Response<List<User>> response) {
                if (response.isSuccessful()) {
                    List<User> users = response.body();
                    StatusCode statusCode = StatusCode.fromValue(response.code());
                    mListener.processUsers(users, new ResponseStatus(statusCode, "User list retrieved successfully."));
                } else {
                    String defaultDetail = "An error occurred while the user list was being retrieved.";
                    ResponseStatus responseStatus = ResponseStatus.createFrom(response, DEFAULT_STATUS_CODE, defaultDetail);
                    Log.e(TAG, responseStatus.getDetail());
                    mListener.processUsers(null, responseStatus);
                }
            }

            @Override
            public void onFailure(@NonNull Call<List<User>> call, @NonNull Throwable t) {
                ResponseStatus responseStatus = new ResponseStatus(DEFAULT_STATUS_CODE, t.getLocalizedMessage());
//                Log.e(TAG, responseStatus.getDetail());
                mListener.processUsers(null, responseStatus);
            }
        });
    }

}
