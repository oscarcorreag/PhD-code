package unimelb.edu.au.ridesharing;

import unimelb.edu.au.ridesharing.rest.StatusCode;

public class ResponseStatus {
    private StatusCode mCode;
    private String mDetail;

    public ResponseStatus(StatusCode mCode, String mDetail) {
        this.mCode = mCode;
        this.mDetail = mDetail;
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
