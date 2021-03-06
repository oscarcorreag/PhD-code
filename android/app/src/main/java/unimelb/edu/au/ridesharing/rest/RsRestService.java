package unimelb.edu.au.ridesharing.rest;

import okhttp3.OkHttpClient;
import okhttp3.logging.HttpLoggingInterceptor;
import retrofit2.Retrofit;
import retrofit2.converter.gson.GsonConverterFactory;
import unimelb.edu.au.ridesharing.BuildConfig;

public class RsRestService {

//    private static final String API_URL = "http://4000L-122353-W:8000/rs/";
//    private static final String API_URL = "http://10.13.196.38:8000";
//    private static final String API_URL = "http://192.168.1.5:8000";
    private static final String API_URL = "http://10.13.206.51:8000";

    private static RsRestServiceI service;

    private static final RsRestService ourInstance = new RsRestService();

    public static RsRestService getInstance() {
        return ourInstance;
    }

    private RsRestService() {

        OkHttpClient.Builder httpClient = new OkHttpClient.Builder();

        // Add a logging interceptor.
        HttpLoggingInterceptor logging = new HttpLoggingInterceptor();
        logging.setLevel(HttpLoggingInterceptor.Level.BODY);
        if (BuildConfig.DEBUG) {
            httpClient.addInterceptor(logging);
        }

        // Add an interceptor for putting authorization headers.
        httpClient.addInterceptor(new BasicAuthInterceptor("naya0105"));

        Retrofit retrofit = new Retrofit.Builder()
                .baseUrl(API_URL)
                .addConverterFactory(GsonConverterFactory.create())
                .client(httpClient.build())
                .build();
        service = retrofit.create(RsRestServiceI.class);
    }

    public RsRestServiceI getService() {
        return service;
    }
}
