package unimelb.edu.au.ridesharing.rest;

import android.support.annotation.NonNull;
import android.util.Log;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;
import unimelb.edu.au.ridesharing.ResponseStatus;

public class FcmController {

    private static final String TAG = FcmController.class.getName();
    private static final StatusCode DEFAULT_STATUS_CODE = StatusCode.INTERNAL_SERVER_ERROR;

    public interface RegistrationFcmControllerListener {
        void processResponseRegistration(ResponseStatus status);
    }

    private RegistrationFcmControllerListener mRegistrationFcmListener;

    public void setRegistrationFcmListener(RegistrationFcmControllerListener registrationFcmListener) {
        this.mRegistrationFcmListener = registrationFcmListener;
    }

    public void sendRegistrationToServer(String userName, String token, String deviceId) {
        Call<ResponseStatus> call = RsRestService.getInstance().getService().sendRegistrationToServer(token, deviceId, "FCM", true, userName);
        call.enqueue(new Callback<ResponseStatus>() {
            @Override
            public void onResponse(@NonNull Call<ResponseStatus> call, @NonNull Response<ResponseStatus> response) {
                if (response.isSuccessful()) {
                    ResponseStatus status = response.body();
                    StatusCode statusCode = StatusCode.fromValue(response.code());
                    assert status != null;
                    status.setCode(statusCode);
                    mRegistrationFcmListener.processResponseRegistration(status);
                } else {
                    String defaultDetail = "An error occurred while registering the token in the App Server.";
                    ResponseStatus responseStatus = ResponseStatus.createFrom(response, DEFAULT_STATUS_CODE, defaultDetail);
                    Log.e(TAG, responseStatus.getDetail());
                    mRegistrationFcmListener.processResponseRegistration(responseStatus);
                }
            }

            @Override
            public void onFailure(@NonNull Call<ResponseStatus> call, @NonNull Throwable t) {
                ResponseStatus responseStatus = new ResponseStatus(DEFAULT_STATUS_CODE, t.getLocalizedMessage());
                mRegistrationFcmListener.processResponseRegistration(responseStatus);
            }
        });
    }
}
