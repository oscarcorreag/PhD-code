package unimelb.edu.au.ridesharing.rest;

import android.support.annotation.NonNull;
import android.util.Log;

import java.io.IOException;
import java.util.List;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;
import unimelb.edu.au.ridesharing.model.Session;

public class SessionController implements Callback<List<Session>> {

    private static final String TAG = "SessionController";

    public interface SessionControllerListener {
        void processSessions(List<Session> sessions);
    }

    private SessionControllerListener mListener;

    public SessionController(SessionControllerListener listener) {
        mListener = listener;
    }

    public void getSessions() {
        Call<List<Session>> call = RsRestService.getInstance().getService().getSessions();
        call.enqueue(this);
    }

    @Override
    public void onResponse(@NonNull Call<List<Session>> call, @NonNull Response<List<Session>> response) {
        if (response.isSuccessful()) {
            List<Session> sessions = response.body();
            mListener.processSessions(sessions);
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
}
