package unimelb.edu.au.ridesharing.rest;

import org.json.JSONObject;

import java.util.List;

import retrofit2.Call;
import retrofit2.http.Body;
import retrofit2.http.FormUrlEncoded;
import retrofit2.http.GET;
import retrofit2.http.POST;
import retrofit2.http.Path;
import retrofit2.http.Query;
import unimelb.edu.au.ridesharing.ResponseStatus;
import unimelb.edu.au.ridesharing.model.KnnNode;
import unimelb.edu.au.ridesharing.model.Session;
import unimelb.edu.au.ridesharing.model.SessionActivity;
import unimelb.edu.au.ridesharing.model.SessionNode;
import unimelb.edu.au.ridesharing.model.SessionUser;
import unimelb.edu.au.ridesharing.model.User;

public interface RsRestServiceI {

    @GET("/rs/knnnodes")
    Call<List<KnnNode>> knnNodes(@Query("longitude") double longitude, @Query("latitude") double latitude, @Query("k") int k);

    @GET("/rs/users")
    Call<List<User>> getUsers();

    @GET("/rs/sessions")
    Call<List<Session>> getSessions();

    @GET("/rs/sessions/can_create")
    Call<ResponseStatus> canCreateSession();

    @POST("/rs/sessions/")
    Call<Session> postSession(@Body Session session);

    @GET("/rs/sessions/{session}/activities")
    Call<List<SessionActivity>> getActivities(@Path("session") int sessionId);

    @POST("/rs/sessions/join/")
    Call<Session> joinSession(@Query("user") int userId);

    @GET("/rs/sessions/{session}/users/{user}")
    Call<SessionUser> getSessionUser(@Path("session") int sessionId, @Path("user") int userId);

    @GET("/rs/sessions/{session}/nodes/?type=P")
    Call<List<SessionNode>> getPois(@Path("session") int sessionId, @Query("activity") String activity);

    @POST("rs/sessions/{session}/plan/")
    Call<ResponseStatus> computePlan(@Path("session") int sessionId, @Query("user") int userId, @Query("activity") String activity);
}
