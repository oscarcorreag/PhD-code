package unimelb.edu.au.ridesharing.rest;

import android.support.annotation.NonNull;
import android.util.Log;

import java.util.List;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;
import unimelb.edu.au.ridesharing.ResponseStatus;
import unimelb.edu.au.ridesharing.model.SessionActivity;

public class SessionActivityController {

    private static final String TAG = "SessionController";
    private static final StatusCode DEFAULT_STATUS_CODE = StatusCode.INTERNAL_SERVER_ERROR;

    public interface ActivityListControllerListener {
        void processActivities(List<SessionActivity> sessions, ResponseStatus status);
    }

    private ActivityListControllerListener mActivityListListener;

    public void setActivityListListener(ActivityListControllerListener activityListListener) {
        this.mActivityListListener = activityListListener;
    }

    public void getActivities(int sessionId) {
        Call<List<SessionActivity>> call = RsRestService.getInstance().getService().getActivities(sessionId);
        call.enqueue(new Callback<List<SessionActivity>>() {
            @Override
            public void onResponse(@NonNull Call<List<SessionActivity>> call, @NonNull Response<List<SessionActivity>> response) {
                if (response.isSuccessful()) {
                    List<SessionActivity> activities = response.body();
                    StatusCode statusCode = StatusCode.fromValue(response.code());
                    mActivityListListener.processActivities(activities, new ResponseStatus(statusCode, "Activity list retrieved successfully."));
                } else {
                    String defaultDetail = "An error occurred while the activity list was being retrieved.";
                    ResponseStatus responseStatus = ResponseStatus.createFrom(response, DEFAULT_STATUS_CODE, defaultDetail);
                    Log.e(TAG, responseStatus.getDetail());
                    mActivityListListener.processActivities(null, responseStatus);
                }
            }

            @Override
            public void onFailure(@NonNull Call<List<SessionActivity>> call, @NonNull Throwable t) {
                ResponseStatus responseStatus = new ResponseStatus(DEFAULT_STATUS_CODE, t.getLocalizedMessage());
//                Log.e(TAG, responseStatus.getDetail());
                mActivityListListener.processActivities(null, responseStatus);
            }
        });
    }
}
