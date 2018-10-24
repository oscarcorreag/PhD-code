package unimelb.edu.au.ridesharing.rest;

import android.support.annotation.NonNull;
import android.util.Log;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;
import java.util.List;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;
import unimelb.edu.au.ridesharing.ResponseStatus;
import unimelb.edu.au.ridesharing.model.Session;

public class SessionController {

    private static final String TAG = "SessionController";

    public interface SessionListControllerListener {
        void processSessions(List<Session> sessions, ResponseStatus status);
    }

    public interface NewSessionControllerListener {
        void processNewSession(Session session, ResponseStatus status);
    }

    private SessionListControllerListener mSessionListListener;
    private NewSessionControllerListener mNewSessionListener;

    public void setSessionListListener(SessionListControllerListener mSessionListListener) {
        this.mSessionListListener = mSessionListListener;
    }

    public void setNewSessionListener(NewSessionControllerListener mNewSessionListener) {
        this.mNewSessionListener = mNewSessionListener;
    }

    public void getSessions() {
        Call<List<Session>> call = RsRestService.getInstance().getService().getSessions();
        call.enqueue(new Callback<List<Session>>() {
            @Override
            public void onResponse(@NonNull Call<List<Session>> call, @NonNull Response<List<Session>> response) {
                if (response.isSuccessful()) {
                    List<Session> sessions = response.body();
                    StatusCode statusCode = StatusCode.valueOf(response.code());
                    mSessionListListener.processSessions(sessions, new ResponseStatus(statusCode, "Session list retrieved successfully."));
                } else {
                    try {
                        Log.e(TAG, response.errorBody().string());
                    } catch (IOException e) {
                        e.printStackTrace();
                    }
                }
            }

            @Override
            public void onFailure(@NonNull Call<List<Session>> call, @NonNull Throwable t) {
                Log.e(TAG, t.getLocalizedMessage());
            }
        });
    }

    public void postSession(Session session) {
        Call<Session> call = RsRestService.getInstance().getService().postSession(session);
        call.enqueue(new Callback<Session>() {
            @Override
            public void onResponse(@NonNull Call<Session> call, @NonNull Response<Session> response) {
                if (response.isSuccessful()) {
                    Session s = response.body();
                    StatusCode statusCode = StatusCode.valueOf(response.code());
                    mNewSessionListener.processNewSession(s, new ResponseStatus(statusCode, "New session was created successfully."));
                } else {
                    StatusCode statusCode = StatusCode.INTERNAL_SERVER_ERROR;
                    String detail = "An error occurred while a new session was being created.";
                    try {
                        JSONObject jsonObject = new JSONObject(response.errorBody().string());
                        int code = jsonObject.getInt("status_code");
                        detail = jsonObject.getString("detail");
                        statusCode = StatusCode.valueOf(code);
                        Log.e(TAG, jsonObject.toString());
                    } catch (IOException | JSONException e) {
                        e.printStackTrace();
                    }
                    mNewSessionListener.processNewSession(null, new ResponseStatus(statusCode, detail));
                }
            }

            @Override
            public void onFailure(@NonNull Call<Session> call, @NonNull Throwable t) {
                Log.e(TAG, t.getLocalizedMessage());
            }
        });
    }

}
