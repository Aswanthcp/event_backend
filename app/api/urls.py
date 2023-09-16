from . import views
from django.urls import path

from rest_framework import permissions


urlpatterns = [

    # admin


    path("admin_login/", views.AdminLogin.as_view(), name="admin_login"),
    path("getUsers/", views.getUsers, name="getUsers"),
    path("getCordinators/", views.getCordinators, name="getCordinators"),
    path("getEvents/", views.getEvents, name="getEvents"),
    path("all_events/", views.getEventsall, name="getEventsall"),
    path("getCategories/", views.getEventTypes, name="getCategories"),
    path("getEventCategory/", views.getEventCategory, name="getEventCategory"),
    path("getCategory/", views.getCategory, name="getCategory"),
    path(
        "getCoordinatorEvents/", views.getCoordinatorEvents, name="getCoordinatorEvents"
    ),
    path(
        "getUserEventBookings/", views.getUserEventBookings, name="getUserEventBookings"
    ),
    path(
        "getUserItemsBookings/", views.getUserItemsBookings, name="getUserItemsBookings"
    ),
    path("getUsers/<id>/", views.getUserbyId,
         name="getUserbyId"),  # geting user by id
    path(
        "getCordinators/<id>/", views.getCordinatorbyId, name="getCordinatorbyId"
    ),  # geting cordinator by id
    # user
    path("signup/", views.signup, name="signup"),
    path("login/", views.login, name="login"),
    # Cordinator
    path("cordinator-signup/", views.cordinator_signup, name="cordinator_signup"),
    path(
        "cordinator-login/", views.CoordinatorLogin.as_view(), name="CoordinatorLogin"
    ),
    path(
        "event_coordinators/",
        views.event_coordinator_list,
        name="event_coordinator_list",
    ),
    path(
        "event_coordinators/<id>",
        views.event_coordinator_detail,
        name="event_coordinator_detail",
    ),
    path(
        "event-cordinator-with-id/<id>",
        views.event_coordinator_detail_with_id,
        name="event_coordinator_detail_with_id",
    ),
    path(
        "event-coordinators-create/",
        views.create_event_coordinator,
        name="create_event_coordinator",
    ),
    path("coordinator/<int:id>", views.Coordinators.as_view(), name="Coordinators"),
    # vender
    path("vender-signup/", views.vender_signup, name="vender_signup"),
    path("vender-login/", views.VenderLogin.as_view(), name="VenderLogin"),
    path("venders/", views.getVenders, name="getVenders"),
    path("venders/<int:id>", views.getVenderbyId, name="getVenderbyId"),
    path("getitem/<int:id>", views.get_all_items_by_supplierID, name="get_all_items"),
    path("items/", views.get_items, name="get-items"),
    #     path('items/<int:id>', views.item_detailbyID, name='item_detailbyID'),
    path("item-create/", views.create_item, name="create_item"),
    path("platoons/", views.get_platoons, name="get-platoons"),
    path("cars/", views.get_cars, name="get-cars"),
    path(
        "flower_decorations/",
        views.get_flower_decorations,
        name="get-flower-decorations",
    ),
    path("floor_mats/", views.get_floor_mats, name="get-floor-mats"),
    path(
        "items/<str:item_type>/<int:id>",
        views.item_detail_by_type,
        name="item_detail_by_type",
    ),
    path(
        "search-coord-users/<str:key>",
        views.SearchCoordinatorUser,
        name="SearchCoordinatorUser",
    ),
    path("block-coord-users/<int:id>",
         views.BlockCordUsers, name="BlockCordUsers"),
    path(
        "unblock-coord-users/<int:id>", views.UnBlockCordUsers, name="UnBlockCordUsers"
    ),
    path(
        "search-venders-users/<str:key>",
        views.SearchVenderUser,
        name="SearchVenderUser",
    ),
    path(
        "block-venders-users/<int:id>",
        views.BlockVendersUsers,
        name="BlockVendersUsers",
    ),
    path(
        "unblock-venders-users/<int:id>",
        views.UnBlockVendersUsers,
        name="UnBlockVendersUsers",
    ),
    path("search-users/<str:key>", views.SearchUser, name="SearchUser"),
    path("block-users/<int:id>", views.BlockUsers, name="BlockUsers"),
    path("unblock-users/<int:id>", views.UnBlockUsers, name="UnBlockUsers"),
    path("search-category/<str:key>", views.SearchCategory, name="SearchCategory"),
    path("search-events/<str:key>", views.SearchEvents, name="SearchEvents"),
    path(
        "search-coordintor-events/<str:key>",
        views.SearchCoordintorEvents,
        name="SearchCoordintorEvents",
    ),
    path(
        "search-category-item/<str:key>",
        views.SearchItemsCategory,
        name="SearchItemsCategory",
    ),
    path(
        "search-user-Events/<str:key>",
        views.SearchUserEventBookings,
        name="SearchUserEventBookings",
    ),
    path(
        "search-user-Items/<str:key>",
        views.SearchUserItemBookings,
        name="SearchUserItemBookings",
    ),
    path(
        "search-supplier-Items/<str:key>",
        views.SearchSuppliersItem,
        name="SearchSuppliersItem",
    ),
    path("getCategories/<int:id>", views.getEventTypesbyId,
         name="getEventTypesbyId"),
    path("getEvents/<int:id>", views.getEventsbyID, name="getEventTypesbyId"),
    path("approveUser/<int:id>", views.approveUser, name="approveUser"),
    path("unapproveUser/<int:id>", views.unapproveUser, name="unapproveUser"),
    path("approveUserItems/<int:id>",
         views.approveUserItems, name="approveUserItems"),
    path(
        "getEventOrders/<int:id>",
        views.UserEventBookingsBycordId,
        name="UserEventBookingsBycordId",
    ),
    path("items-users-Booking/", views.user_item_Booking, name="user_item_Booking"),
    path(
        "items-BookingLists/<int:id>",
        views.user_Booking_list_by_Suppler_id,
        name="user_Booking_list_by_Suppler_id",
    ),
    path(
        "items-user-suppleir-PaidLists/<int:id>",
        views.user_Paid_list_by_Suppler_id,
        name="user_Paid_list_by_Suppler_id",
    ),
    path(
        "items-PaidList/<int:id>",
        views.paidBookingListbyUserId,
        name="paidBookingListbyUserId",
    ),
    path(
        "approve-item-bookings/<int:id>",
        views.approvedBookingListbyUserId,
        name="approvedBookingListbyUserId",
    ),
    path(
        "non-approve-item-bookings/<int:id>",
        views.unapprovedBookingListbyUserId,
        name="unapprovedBookingListbyUserId",
    ),
    path(
        "paid-item-bookings/<int:id>",
        views.paidBookingListbyUserId,
        name="paidBookingListbyUserId",
    ),
    path("verify-payment/", views.verify_payment, name="verify_payment"),
    path(
        "verify-event-payment/", views.verify_event_payment, name="verify_event_payment"
    ),
    path(
        "create-checkout-session/",
        views.create_checkout_session,
        name="create_checkout_session",
    ),
    #     event management user Booking
    #     path("event-users/<int:id>", views.getEventOrders, name="getEventOrders"),
    path("event-users-Booking/", views.events_user_Booking,
         name="events_user_Booking"),
    path(
        "event-user-book/<int:pk>/",
        views.EventUserBookDetailView.as_view(),
        name="event-user-book-detail",
    ),
    path(
        "approve-event-bookings/<int:id>",
        views.approvedEventBookingListbyUserId,
        name="approvedEventBookingListbyUserId",
    ),
    path(
        "approve-event-bookings-Supplier/<int:id>",
        views.approvedEventBookingListbysupplierId,
        name="approvedEventBookingListbysupplierId",
    ),
    path(
        "nonapprove-event-bookings-Supplier/<int:id>",
        views.nonapprovedEventBookingListbysupplierId,
        name="nonapprovedEventBookingListbysupplierId",
    ),
    path(
        "paid-event-bookings-Supplier/<int:id>",
        views.PaidEventBookingListbysupplierId,
        name="PaidEventBookingListbysupplierId",
    ),
    path(
        "non-approve-event-bookings/<int:id>",
        views.unapprovedEventBookingListbyUserId,
        name="unapprovedEventBookingListbyUserId",
    ),
    path(
        "paid-event-bookings/<int:id>",
        views.paidEventBookingListbyUserId,
        name="paidEventBookingListbyUserId",
    ),
    #     item orders
    path(
        "getItemorder-by-date/<str:date>",
        views.get_Itemorders_by_date,
        name="get_Itemorders_by_date",
    ),
    path(
        "getItemorder-by-admin/<str:date>",
        views.get_daily_revenue_admin,
        name="get_Itemorders_by_date",
    ),
    path(
        "getItemorder-monthly/",
        views.get_Itemmonthly_revenue,
        name="get_Itemmonthly_revenue",
    ),
    path(
        "getItemorder-monthly-by-admin/",
        views.get_monthly_revenue_by_admin,
        name="get_monthly_revenue_by_admin",
    ),
    path(
        "getItemorder-yearly/",
        views.get_Itemyearly_revenue,
        name="get_Itemyearly_revenue",
    ),
    path(
        "getItemorder-weekly/",
        views.get_Itemweekly_revenue,
        name="get_Itemweekly_revenue",
    ),
    #     Event orders
    path(
        "getEventorder/<str:date>",
        views.get_Eventorders_by_date,
        name="getEventorderby_date",
    ),
    path(
        "getEventorder-by-admin/<str:date>",
        views.get_daily_revenue_admin,
        name="getEventorderby_date",
    ),
    path(
        "getEventorder-monthly/", views.get_monthly_revenue, name="get_monthly_revenue"
    ),
    path("getEventorder-yearly/", views.get_yearly_revenue,
         name="get_yearly_revenue"),
    path("getEventorder-weekly/", views.get_weekly_revenue,
         name="get_weekly_revenue"),
    path(
        "coordintorbooking-count/<int:id>",
        views.coordinator_booking_count,
        name="coordinator_booking_count",
    ),
    path(
        "coordintorevent-count/<int:id>",
        views.coordinator_events_count,
        name="coordinator_events_count",
    ),
    path(
        "coordintorevent-price/<int:id>",
        views.coordinator_earning,
        name="coordinator_earning",
    ),
    path(
        "supplierBooking-count/<int:id>",
        views.supplier_booking_count,
        name="supplier_booking_count",
    ),
    path(
        "supplierItems-count/<int:id>",
        views.supplier_Items_count,
        name="supplier_Items_count",
    ),
    path(
        "supplierItems-price/<int:id>", views.supplier_earning, name="supplier_earning"
    ),
]
