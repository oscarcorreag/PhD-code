package unimelb.edu.au.ridesharing.rest;

import java.util.List;

import retrofit2.Call;
import retrofit2.http.Body;
import retrofit2.http.FormUrlEncoded;
import retrofit2.http.GET;
import retrofit2.http.POST;
import retrofit2.http.Path;
import retrofit2.http.Query;
import unimelb.edu.au.ridesharing.model.KnnNode;
import unimelb.edu.au.ridesharing.model.Session;
import unimelb.edu.au.ridesharing.model.SessionActivity;
import unimelb.edu.au.ridesharing.model.SessionUser;
import unimelb.edu.au.ridesharing.model.User;

public interface RsRestServiceI {

    @GET("/rs/knnnodes")
    Call<List<KnnNode>> knnNodes(@Query("longitude") double longitude, @Query("latitude") double latitude, @Query("k") int k);

    @GET("/rs/users")
    Call<List<User>> getUsers();

    @GET("/rs/sessions")
    Call<List<Session>> getSessions();

    @POST("/rs/sessions/")
    Call<Session> postSession(@Body Session session);

    @GET("/rs/sessions/{session}/activities")
    Call<List<SessionActivity>> getActivities(@Path("session") int sessionId);

    @POST("/rs/sessions/join/")
    Call<Session> joinSession(@Query("user") int userId);

    @GET("/rs/sessions/{session}/users/{user}")
    Call<SessionUser> getSessionUser(@Path("session") int sessionId, @Path("user") int userId);

    @POST("rs/session/{session}/plan/")
    Call<Session> plan(@Path("session") int sessionId, @Query("user") int userId, @Query("activity") String activity);
}
