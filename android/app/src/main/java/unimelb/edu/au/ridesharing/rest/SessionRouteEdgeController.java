package unimelb.edu.au.ridesharing.rest;

import android.support.annotation.NonNull;
import android.util.Log;

import java.util.List;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;
import unimelb.edu.au.ridesharing.ResponseStatus;
import unimelb.edu.au.ridesharing.model.SessionRouteEdge;

public class SessionRouteEdgeController {

    private static final String TAG = SessionRouteEdgeController.class.getName();
    private static final StatusCode DEFAULT_STATUS_CODE = StatusCode.INTERNAL_SERVER_ERROR;

    public interface SessionRouteControllerListener {
        void processSessionRoute(List<SessionRouteEdge> route, ResponseStatus status);
    }

    private SessionRouteControllerListener mSssionRouteListener;

    public void setSessionRouteListener(SessionRouteControllerListener sessionRouteListener) {
        this.mSssionRouteListener = sessionRouteListener;
    }

    public void getSessionRoute(String userName, int sessionUserId) {
        Call<List<SessionRouteEdge>> call = RsRestService.getInstance().getService().getSessionRoute(userName, sessionUserId);
        call.enqueue(new Callback<List<SessionRouteEdge>>() {
            @Override
            public void onResponse(@NonNull Call<List<SessionRouteEdge>> call, @NonNull Response<List<SessionRouteEdge>> response) {
                if (response.isSuccessful()) {
                    List<SessionRouteEdge> route = response.body();
                    StatusCode statusCode = StatusCode.fromValue(response.code());
                    mSssionRouteListener.processSessionRoute(route, new ResponseStatus(statusCode, "Session route was retrieved successfully."));
                } else {
                    String defaultDetail = "An error occurred while the session route was being retrieved.";
                    ResponseStatus responseStatus = ResponseStatus.createFrom(response, DEFAULT_STATUS_CODE, defaultDetail);
                    Log.e(TAG, responseStatus.getDetail());
                    mSssionRouteListener.processSessionRoute(null, responseStatus);
                }
            }

            @Override
            public void onFailure(@NonNull Call<List<SessionRouteEdge>> call, @NonNull Throwable t) {
                ResponseStatus responseStatus = new ResponseStatus(DEFAULT_STATUS_CODE, t.getLocalizedMessage());
//                Log.e(TAG, responseStatus.getDetail());
                mSssionRouteListener.processSessionRoute(null, responseStatus);
            }
        });
    }
}
