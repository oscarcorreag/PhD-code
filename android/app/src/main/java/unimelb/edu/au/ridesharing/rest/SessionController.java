package unimelb.edu.au.ridesharing.rest;

import android.support.annotation.NonNull;
import android.util.Log;

import java.util.List;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;
import unimelb.edu.au.ridesharing.ResponseStatus;
import unimelb.edu.au.ridesharing.model.Session;

public class SessionController {

    private static final String TAG = "SessionController";
    private static final StatusCode DEFAULT_STATUS_CODE = StatusCode.INTERNAL_SERVER_ERROR;

    public interface SessionListControllerListener {
        void processSessions(List<Session> sessions, ResponseStatus status);
    }

    public interface NewSessionControllerListener {
        void processNewSession(Session session, ResponseStatus status);
    }

    public interface JoinSessionControllerListener {
        void processActiveSession(Session session, ResponseStatus status);
    }

    private SessionListControllerListener mSessionListListener;
    private NewSessionControllerListener mNewSessionListener;
    private JoinSessionControllerListener mJoinSessionListener;

    public void setSessionListListener(SessionListControllerListener sessionListListener) {
        this.mSessionListListener = sessionListListener;
    }

    public void setNewSessionListener(NewSessionControllerListener newSessionListener) {
        this.mNewSessionListener = newSessionListener;
    }

    public void setJoinSessionListener(JoinSessionControllerListener joinSessionListener) {
        this.mJoinSessionListener = joinSessionListener;
    }

    public void getSessions() {
        Call<List<Session>> call = RsRestService.getInstance().getService().getSessions();
        call.enqueue(new Callback<List<Session>>() {
            @Override
            public void onResponse(@NonNull Call<List<Session>> call, @NonNull Response<List<Session>> response) {
                if (response.isSuccessful()) {
                    List<Session> sessions = response.body();
                    StatusCode statusCode = StatusCode.fromValue(response.code());
                    mSessionListListener.processSessions(sessions, new ResponseStatus(statusCode, "Session list retrieved successfully."));
                } else {
                    String defaultDetail = "An error occurred while the session list was being retrieved.";
                    mSessionListListener.processSessions(null, ResponseStatus.createFrom(response, DEFAULT_STATUS_CODE, defaultDetail));
                }
            }

            @Override
            public void onFailure(@NonNull Call<List<Session>> call, @NonNull Throwable t) {
                Log.e(TAG, t.getLocalizedMessage());
                mSessionListListener.processSessions(null, new ResponseStatus(DEFAULT_STATUS_CODE, t.getLocalizedMessage()));
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
                    StatusCode statusCode = StatusCode.fromValue(response.code());
                    mNewSessionListener.processNewSession(s, new ResponseStatus(statusCode, "New session was created successfully."));
                } else {
                    String defaultDetail = "An error occurred while a new session was being created.";
                    ResponseStatus responseStatus = ResponseStatus.createFrom(response, DEFAULT_STATUS_CODE, defaultDetail);
                    Log.e(TAG, responseStatus.getDetail());
                    mNewSessionListener.processNewSession(null, responseStatus);
                }
            }

            @Override
            public void onFailure(@NonNull Call<Session> call, @NonNull Throwable t) {
                ResponseStatus responseStatus = new ResponseStatus(DEFAULT_STATUS_CODE, t.getLocalizedMessage());
                Log.e(TAG, responseStatus.getDetail());
                // TODO: Since this seems to be a client-side error, e.g., timeout, it may be possible a session was indeed created. Therefore, reloading is an option. UPDATE: However, this can be workarounded by joining to active session.
                mNewSessionListener.processNewSession(null, responseStatus);
            }
        });
    }

    public void joinSession(int userId) {
        Call<Session> call = RsRestService.getInstance().getService().joinSession(userId);
        call.enqueue(new Callback<Session>() {
            @Override
            public void onResponse(@NonNull Call<Session> call, @NonNull Response<Session> response) {
                if (response.isSuccessful()) {
                    Session s = response.body();
                    StatusCode statusCode = StatusCode.fromValue(response.code());
                    mJoinSessionListener.processActiveSession(s, new ResponseStatus(statusCode, "User joined the active session."));
                } else {
                    String defaultDetail = "An error occurred while user tried to join the active session.";
                    ResponseStatus responseStatus = ResponseStatus.createFrom(response, DEFAULT_STATUS_CODE, defaultDetail);
                    Log.e(TAG, responseStatus.getDetail());
                    mJoinSessionListener.processActiveSession(null, responseStatus);
                }
            }

            @Override
            public void onFailure(@NonNull Call<Session> call, @NonNull Throwable t) {
                ResponseStatus responseStatus = new ResponseStatus(DEFAULT_STATUS_CODE, t.getLocalizedMessage());
                Log.e(TAG, responseStatus.getDetail());
                mJoinSessionListener.processActiveSession(null, responseStatus);
            }
        });
    }

}
