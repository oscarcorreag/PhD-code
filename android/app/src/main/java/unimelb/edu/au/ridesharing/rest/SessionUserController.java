package unimelb.edu.au.ridesharing.rest;

import android.support.annotation.NonNull;
import android.util.Log;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;
import unimelb.edu.au.ridesharing.ResponseStatus;
import unimelb.edu.au.ridesharing.model.SessionUser;

public class SessionUserController {

    private static final String TAG = "SessionUserController";
    private static final StatusCode DEFAULT_STATUS_CODE = StatusCode.INTERNAL_SERVER_ERROR;

    public interface SessionUserControllerListener {
        void processSessionUser(SessionUser sessionUser, ResponseStatus status);
    }

    private SessionUserControllerListener mSessionUserListener;

    public void setSessionUserListener(SessionUserControllerListener sessionUserListener) {
        this.mSessionUserListener = sessionUserListener;
    }

    public void getUser(int sessionId, int userId) {
        Call<SessionUser> call = RsRestService.getInstance().getService().getSessionUser(sessionId, userId);
        call.enqueue(new Callback<SessionUser>() {
            @Override
            public void onResponse(@NonNull Call<SessionUser> call, @NonNull Response<SessionUser> response) {
                if (response.isSuccessful()) {
                    SessionUser su = response.body();
                    StatusCode statusCode = StatusCode.fromValue(response.code());
                    mSessionUserListener.processSessionUser(su, new ResponseStatus(statusCode, "Session user was retrieved successfully."));
                } else {
                    String defaultDetail = "An error occurred while the session user was being retrieved.";
                    ResponseStatus responseStatus = ResponseStatus.createFrom(response, DEFAULT_STATUS_CODE, defaultDetail);
                    Log.e(TAG, responseStatus.getDetail());
                    mSessionUserListener.processSessionUser(null, responseStatus);

                }
            }

            @Override
            public void onFailure(@NonNull Call<SessionUser> call, @NonNull Throwable t) {
                ResponseStatus responseStatus = new ResponseStatus(DEFAULT_STATUS_CODE, t.getLocalizedMessage());
//                Log.e(TAG, responseStatus.getDetail());
                mSessionUserListener.processSessionUser(null, responseStatus);
            }
        });
    }
}
