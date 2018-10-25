package unimelb.edu.au.ridesharing;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;

import retrofit2.Response;
import unimelb.edu.au.ridesharing.rest.StatusCode;

public class ResponseStatus {
    private StatusCode mCode;
    private String mDetail;

    public ResponseStatus(StatusCode mCode, String mDetail) {
        this.mCode = mCode;
        this.mDetail = mDetail;
    }

    public ResponseStatus(JSONObject jsonObject) {
        try {
            this.mCode = StatusCode.fromValue(jsonObject.getInt("status_code"));
            this.mDetail = jsonObject.getString("detail");
        } catch (JSONException e) {
            this.mCode = StatusCode.INTERNAL_SERVER_ERROR;
            this.mDetail = "Unknown error.";
        }
    }

    public static ResponseStatus createFrom(Response response, StatusCode defaultCode, String defaultDetail) {
        ResponseStatus responseStatus = null;
        try {
            JSONObject jsonObject = new JSONObject(response.errorBody().string());
            responseStatus = new ResponseStatus(jsonObject);
        } catch (IOException | JSONException e) {
            e.printStackTrace();
        }
        if (responseStatus == null) {
            responseStatus = new ResponseStatus(defaultCode, defaultDetail);
        }
        return responseStatus;
    }

    public StatusCode getCode() {
        return mCode;
    }

    public void setCode(StatusCode code) {
        this.mCode = code;
    }

    public String getDetail() {
        return mDetail;
    }

    public void setDetail(String detail) {
        this.mDetail = detail;
    }

    public boolean isSuccessful() {
        return this.mCode.getCode() >= 200 && this.mCode.getCode() < 300;
    }
}
