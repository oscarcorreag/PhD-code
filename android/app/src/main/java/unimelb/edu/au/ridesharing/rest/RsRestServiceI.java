package unimelb.edu.au.ridesharing.rest;

import java.util.List;

import retrofit2.Call;
import retrofit2.http.Body;
import retrofit2.http.Field;
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
import unimelb.edu.au.ridesharing.model.SessionRouteEdge;
import unimelb.edu.au.ridesharing.model.SessionUser;
import unimelb.edu.au.ridesharing.model.User;

public interface RsRestServiceI {

    @GET("/rs/knnnodes")
    Call<List<KnnNode>> knnNodes(@Query("longitude") double longitude, @Query("latitude") double latitude, @Query("k") int k);

    @GET("/rs/users")
    Call<List<User>> getUsers(@Query("username") String userName);

    @GET("/rs/sessions")
    Call<List<Session>> getSessions(@Query("username") String userName);

    @GET("/rs/sessions/can_create")
    Call<ResponseStatus> canCreateSession(@Query("username") String userName);

    @POST("/rs/sessions/")
    Call<Session> postSession(@Query("username") String userName, @Body Session session);

    @GET("/rs/sessions/{session}/activities")
    Call<List<SessionActivity>> getActivities(@Path("session") int sessionId, @Query("username") String userName);

    @POST("/rs/sessions/join/")
    Call<Session> joinSession(@Query("username") String userName, @Query("user") int userId);

    @POST("/rs/sessions/end/")
    Call<ResponseStatus> endSession(@Query("username") String userName, @Query("user") int userId);

    @GET("/rs/sessions/{session}/users/{user}")
    Call<SessionUser> getSessionUser(@Path("session") int sessionId, @Path("user") int userId, @Query("username") String userName);

    @GET("/rs/sessions/{session}/nodes/?type=P")
    Call<List<SessionNode>> getPois(@Path("session") int sessionId, @Query("activity") String activity, @Query("username") String userName);

    @POST("rs/sessions/{session}/plan/")
    Call<ResponseStatus> computePlan(@Path("session") int sessionId, @Query("user") int userId, @Query("activity") String activity, @Query("username") String userName);

    @FormUrlEncoded
    @POST("/rs/device/gcm/")
    Call<ResponseStatus> sendRegistrationToServer(
            @Field("registration_id") String token,
            @Field("device_id") String deviceId,
            @Field("cloud_message_type") String messageType,
            @Field("active") boolean isActive,
            @Query("username") String userName);

    @GET("rs/route")
    Call<List<SessionRouteEdge>> getSessionRoute(@Query("username") String userName, @Query("user") int sessionUserId);

    @GET("/rs/sessions/{session}/users/routemates")
    Call<List<SessionUser>> getRouteMates(@Path("session") int sessionId, @Query("user") int userId, @Query("username") String userName);
}
