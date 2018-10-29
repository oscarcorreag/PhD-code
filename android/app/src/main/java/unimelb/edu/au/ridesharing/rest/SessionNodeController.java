package unimelb.edu.au.ridesharing.rest;

import android.support.annotation.NonNull;
import android.util.Log;

import java.util.List;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;
import unimelb.edu.au.ridesharing.ResponseStatus;
import unimelb.edu.au.ridesharing.model.SessionNode;

public class SessionNodeController {

    private static final String TAG = "SessionNodeController";
    private static final StatusCode DEFAULT_STATUS_CODE = StatusCode.INTERNAL_SERVER_ERROR;

    public interface PoisListener {
        void processPois(List<SessionNode> pois, ResponseStatus status);
    }

    private PoisListener mPoisListener;

    public void setPoisListener(PoisListener poisListener) {
        this.mPoisListener = poisListener;
    }

    public void getPois(int sessionId, String activity) {
        Call<List<SessionNode>> call = RsRestService.getInstance().getService().getPois(sessionId, activity);
        call.enqueue(new Callback<List<SessionNode>>() {
            @Override
            public void onResponse(@NonNull Call<List<SessionNode>> call, @NonNull Response<List<SessionNode>> response) {
                if (response.isSuccessful()) {
                    List<SessionNode> pois = response.body();
                    StatusCode statusCode = StatusCode.fromValue(response.code());
                    mPoisListener.processPois(pois, new ResponseStatus(statusCode, "POIs retrieved successfully."));
                } else {
                    String defaultDetail = "An error occurred while the POIs were being retrieved.";
                    ResponseStatus responseStatus = ResponseStatus.createFrom(response, DEFAULT_STATUS_CODE, defaultDetail);
                    Log.e(TAG, responseStatus.getDetail());
                    mPoisListener.processPois(null, responseStatus);
                }
            }

            @Override
            public void onFailure(@NonNull Call<List<SessionNode>> call, @NonNull Throwable t) {
                ResponseStatus responseStatus = new ResponseStatus(DEFAULT_STATUS_CODE, t.getLocalizedMessage());
                mPoisListener.processPois(null, responseStatus);
            }
        });
    }
}
