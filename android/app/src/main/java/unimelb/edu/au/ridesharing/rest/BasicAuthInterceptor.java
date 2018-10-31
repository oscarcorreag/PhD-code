package unimelb.edu.au.ridesharing.rest;

import android.support.annotation.NonNull;
import android.util.Log;

import java.io.IOException;

import okhttp3.Credentials;
import okhttp3.Interceptor;
import okhttp3.Request;
import okhttp3.Response;

public class BasicAuthInterceptor implements Interceptor {

    private final static String TAG = BasicAuthInterceptor.class.getName();

    private String mPassword;

    BasicAuthInterceptor(String password) {
        this.mPassword = password;
    }

    @Override
    public Response intercept(@NonNull Chain chain) throws IOException {
        Request request = chain.request();
        String userName = request.url().queryParameter("username");
        assert userName != null;
        String credentials = Credentials.basic(userName, mPassword);
        Request authenticatedRequest = request.newBuilder().header("Authorization", credentials).build();
        return chain.proceed(authenticatedRequest);
    }
}
